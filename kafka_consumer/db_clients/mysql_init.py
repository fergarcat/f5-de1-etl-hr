from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os

# 1. Cargar variables de entorno
load_dotenv()
mysql_user = os.getenv('MYSQL_INITDB_ROOT_USERNAME')
mysql_password = os.getenv('MYSQL_INITDB_ROOT_PASSWORD')
mysql_host = os.getenv('MYSQL_HOST', 'localhost')
mysql_database = os.getenv('MYSQL_DATABASE')


# 2. Crear motor de conexión
mysql_uri = f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_database}"
engine = create_engine(mysql_uri)

# 3. Declarar base y modelo
Base = declarative_base()

class Evento(Base):
    __tablename__ = 'eventos'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(255), nullable=False)
    timestamp = Column(DateTime, nullable=True)

# 4. Crear tablas si no existen
try:
    Base.metadata.create_all(engine)
    print("✅ Tables created successfully.")
except Exception as e:
    print(f"❌ Error creating tables: {e}")
