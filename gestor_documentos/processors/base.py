from abc import ABC, abstractmethod

class DocumentProcessor(ABC):
    """Clase base para procesadores de documentos"""
    
    @abstractmethod
    def process(self, file):
        """Procesa el archivo y retorna los datos extraídos"""
        pass
    
    @abstractmethod
    def get_metadata(self):
        """Retorna metadatos del documento procesado"""
        pass
