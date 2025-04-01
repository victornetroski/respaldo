import os

def init_db():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from .db.models import Base
    
    db_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db')
    os.makedirs(db_dir, exist_ok=True)
    db_path = f'sqlite:///{os.path.join(db_dir, "cfdi.db")}'
    
    engine = create_engine(db_path)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()
