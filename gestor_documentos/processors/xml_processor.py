import xml.etree.ElementTree as ET
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from .base import DocumentProcessor
from ..db.models import CFDI, Concepto, Impuesto, ImpuestoConcepto

class CFDIProcessor(DocumentProcessor):
    """Procesador específico para CFDI (XML)"""
    
    def __init__(self, db_session: Session):
        self.namespaces = {
            'cfdi': 'http://www.sat.gob.mx/cfd/4',
            'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'
        }
        self.data = None
        self.db_session = db_session

    def process(self, file):
        try:
            tree = ET.parse(file)
            root = tree.getroot()
            
            # Extraer datos con manejo de errores para campos opcionales
            self.data = {
                'comprobante': root.attrib,
                'emisor': root.find('cfdi:Emisor', self.namespaces).attrib if root.find('cfdi:Emisor', self.namespaces) is not None else {},
                'receptor': root.find('cfdi:Receptor', self.namespaces).attrib if root.find('cfdi:Receptor', self.namespaces) is not None else {},
                'conceptos': [
                    {
                        **concepto.attrib,
                        'impuestos': {
                            'traslados': [
                                traslado.attrib for traslado in concepto.findall('cfdi:Impuestos/cfdi:Traslados/cfdi:Traslado', self.namespaces)
                            ],
                            'retenciones': [
                                retencion.attrib for retencion in concepto.findall('cfdi:Impuestos/cfdi:Retenciones/cfdi:Retencion', self.namespaces)
                            ]
                        } if concepto.find('cfdi:Impuestos', self.namespaces) is not None else None
                    }
                    for concepto in root.findall('cfdi:Conceptos/cfdi:Concepto', self.namespaces)
                ],
                'impuestos': self._extract_impuestos(root),
                'timbre': root.find('.//tfd:TimbreFiscalDigital', self.namespaces).attrib if root.find('.//tfd:TimbreFiscalDigital', self.namespaces) is not None else {}
            }
            
            # Guardar en la base de datos
            self._save_to_db()
            return self.data
        except Exception as e:
            print(f"Error procesando XML: {str(e)}")
            raise

    def _extract_impuestos(self, root):
        impuestos = root.find('cfdi:Impuestos', self.namespaces)
        if impuestos is None:
            return None
        
        return {
            'total_impuestos_trasladados': impuestos.get('TotalImpuestosTrasladados'),
            'total_impuestos_retenidos': impuestos.get('TotalImpuestosRetenidos'),
            'traslados': [
                traslado.attrib 
                for traslado in impuestos.findall('cfdi:Traslados/cfdi:Traslado', self.namespaces)
            ],
            'retenciones': [
                retencion.attrib 
                for retencion in impuestos.findall('cfdi:Retenciones/cfdi:Retencion', self.namespaces)
            ]
        }

    def _save_to_db(self):
        """Guarda los datos del CFDI en la base de datos"""
        if not self.data:
            return

        # Verificar si el CFDI ya existe
        uuid = self.data['timbre']['UUID']
        existing_cfdi = self.db_session.execute(
            select(CFDI).where(CFDI.uuid == uuid)
        ).scalar_one_or_none()

        if existing_cfdi:
            # Si ya existe, actualizar en lugar de insertar
            self.db_session.query(CFDI).filter_by(uuid=uuid).update({
                'fecha': datetime.fromisoformat(self.data['comprobante']['Fecha']),
                'total': float(self.data['comprobante']['Total']),
                'subtotal': float(self.data['comprobante']['SubTotal']),
                'emisor_rfc': self.data['emisor']['Rfc'],
                'emisor_nombre': self.data['emisor']['Nombre'],
                'receptor_rfc': self.data['receptor']['Rfc'],
                'receptor_nombre': self.data['receptor']['Nombre']
            })
            cfdi = existing_cfdi
        else:
            # Si no existe, crear nuevo
            cfdi = CFDI(
                uuid=uuid,
                fecha=datetime.fromisoformat(self.data['comprobante']['Fecha']),
                total=float(self.data['comprobante']['Total']),
                subtotal=float(self.data['comprobante']['SubTotal']),
                emisor_rfc=self.data['emisor']['Rfc'],
                emisor_nombre=self.data['emisor']['Nombre'],
                receptor_rfc=self.data['receptor']['Rfc'],
                receptor_nombre=self.data['receptor']['Nombre']
            )
            self.db_session.add(cfdi)
            
        try:
            self.db_session.flush()

            # Eliminar conceptos e impuestos existentes si estamos actualizando
            if existing_cfdi:
                self.db_session.query(Concepto).filter_by(cfdi_id=cfdi.id).delete()
                self.db_session.query(Impuesto).filter_by(cfdi_id=cfdi.id).delete()

            # Guardar conceptos
            for concepto_data in self.data['conceptos']:
                concepto = Concepto(
                    cfdi_id=cfdi.id,
                    clave_prod_serv=concepto_data['ClaveProdServ'],
                    cantidad=float(concepto_data['Cantidad']),
                    descripcion=concepto_data['Descripcion'],
                    valor_unitario=float(concepto_data['ValorUnitario']),
                    importe=float(concepto_data['Importe'])
                )
                self.db_session.add(concepto)
                
                # Guardar impuestos del concepto
                if concepto_data.get('impuestos'):
                    self._save_concepto_impuestos(concepto, concepto_data['impuestos'])
            
            # Guardar impuestos generales
            if self.data.get('impuestos'):
                self._save_impuestos(cfdi, self.data['impuestos'])
            
            self.db_session.commit()
        except Exception as e:
            self.db_session.rollback()
            raise e

    def _save_concepto_impuestos(self, concepto, impuestos_data):
        for traslado in impuestos_data.get('traslados', []):
            try:
                impuesto = ImpuestoConcepto(
                    concepto_id=concepto.id,
                    tipo='traslado',
                    impuesto=traslado.get('Impuesto', ''),
                    base=float(traslado.get('Base', 0)),
                    tasa=float(traslado.get('TasaOCuota', 0) or traslado.get('TasaCuota', 0) or 0),
                    importe=float(traslado.get('Importe', 0))
                )
                self.db_session.add(impuesto)
            except (ValueError, AttributeError) as e:
                print(f"Error procesando impuesto de concepto: {str(e)}")
                continue

    def _save_impuestos(self, cfdi, impuestos_data):
        for traslado in impuestos_data.get('traslados', []):
            try:
                impuesto = Impuesto(
                    cfdi_id=cfdi.id,
                    tipo='traslado',
                    impuesto=traslado.get('Impuesto', ''),
                    base=float(traslado.get('Base', 0)),
                    tasa=float(traslado.get('TasaOCuota', 0) or traslado.get('TasaCuota', 0) or 0),
                    importe=float(traslado.get('Importe', 0))
                )
                self.db_session.add(impuesto)
            except (ValueError, AttributeError) as e:
                print(f"Error procesando impuesto: {str(e)}")
                continue

    def get_metadata(self):
        """Retorna información clave del CFDI"""
        if not self.data:
            return None
        
        return {
            'uuid': self.data['timbre']['UUID'],
            'total': self.data['comprobante']['Total'],
            'emisor_rfc': self.data['emisor']['Rfc'],
            'emisor_nombre': self.data['emisor']['Nombre'],
            'receptor_rfc': self.data['receptor']['Rfc'],
            'receptor_nombre': self.data['receptor']['Nombre'],
            'fecha': self.data['comprobante']['Fecha']
        }

    # Métodos de ayuda para acceder a datos específicos
    def get_uuid(self):
        return self.data['timbre']['UUID'] if self.data else None

    def get_total(self):
        return self.data['comprobante']['Total'] if self.data else None

    def get_conceptos(self):
        return self.data['conceptos'] if self.data else None

    def get_value(self, path):
        """
        Obtiene un valor específico del CFDI usando una ruta de acceso.
        Ejemplo: get_value('comprobante.Total') o get_value('emisor.Rfc')
        """
        if not self.data:
            return None

        parts = path.lower().split('.')
        current = self.data
        try:
            for part in parts:
                if isinstance(current, dict):
                    # Buscar la clave ignorando mayúsculas/minúsculas
                    key = next(k for k in current.keys() if k.lower() == part)
                    current = current[key]
                elif isinstance(current, list):
                    current = current[int(part)]
                else:
                    return None
            return current
        except (KeyError, IndexError, StopIteration):
            return None

    def get_concepto(self, index):
        """Obtiene un concepto específico por su índice"""
        if not self.data or not self.data['conceptos']:
            return None
        try:
            return self.data['conceptos'][index]
        except IndexError:
            return None
