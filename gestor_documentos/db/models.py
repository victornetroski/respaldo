from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class CFDI(Base):
    __tablename__ = 'cfdis'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(String, unique=True)
    fecha = Column(DateTime)
    total = Column(Float)
    subtotal = Column(Float)
    
    # Datos del emisor
    emisor_rfc = Column(String)
    emisor_nombre = Column(String)
    
    # Datos del receptor
    receptor_rfc = Column(String)
    receptor_nombre = Column(String)
    
    # Relaciones
    conceptos = relationship("Concepto", back_populates="cfdi")
    impuestos = relationship("Impuesto", back_populates="cfdi")

class Concepto(Base):
    __tablename__ = 'conceptos'
    
    id = Column(Integer, primary_key=True)
    cfdi_id = Column(Integer, ForeignKey('cfdis.id'))
    clave_prod_serv = Column(String)
    cantidad = Column(Float)
    descripcion = Column(String)
    valor_unitario = Column(Float)
    importe = Column(Float)
    
    cfdi = relationship("CFDI", back_populates="conceptos")
    impuestos = relationship("ImpuestoConcepto", back_populates="concepto")

class Impuesto(Base):
    __tablename__ = 'impuestos'
    
    id = Column(Integer, primary_key=True)
    cfdi_id = Column(Integer, ForeignKey('cfdis.id'))
    tipo = Column(String)  # 'traslado' o 'retencion'
    impuesto = Column(String)
    base = Column(Float)
    tasa = Column(Float)
    importe = Column(Float)
    
    cfdi = relationship("CFDI", back_populates="impuestos")

class ImpuestoConcepto(Base):
    __tablename__ = 'impuestos_conceptos'
    
    id = Column(Integer, primary_key=True)
    concepto_id = Column(Integer, ForeignKey('conceptos.id'))
    tipo = Column(String)
    impuesto = Column(String)
    base = Column(Float)
    tasa = Column(Float)
    importe = Column(Float)
    
    concepto = relationship("Concepto", back_populates="impuestos")
