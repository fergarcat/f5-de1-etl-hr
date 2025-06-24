from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
from dotenv import load_dotenv
import os

# 1. Cargar variables de entorno
load_dotenv()
mysql_user = os.getenv('MYSQL_USER')
mysql_password = os.getenv('MYSQL_PASSWORD')
mysql_host = os.getenv('MYSQL_HOST')
mysql_database = os.getenv('MYSQL_DATABASE')



# 2. Create connection without specifying the databaseAdd commentMore actions
mysql_port = os.getenv('MYSQL_PORT', '3306')
mysql_uri_no_db = f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/"
engine_no_db = create_engine(mysql_uri_no_db, echo=True)

# 3. Create the database if it does not exist
with engine_no_db.connect() as conn:
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {mysql_database}"))
    conn.commit()


# 4. Create the connection engine with the database
mysql_uri = f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"
engine = create_engine(mysql_uri, echo=False)

# 5. Declare base and models
Base = declarative_base()

class Profile(Base):
    __tablename__ = 'profiles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String(255), unique=True, nullable=False)
    name = Column(String(255))
    email = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - CORREGIDO
    personal = relationship("Personal", back_populates="profile", uselist=False)
    address = relationship("Address", back_populates="profile", uselist=False)
    professional = relationship("Professional", back_populates="profile", uselist=False)
    bank = relationship("Bank", back_populates="profile", uselist=False)
    network = relationship("Network", back_populates="profile", uselist=False)

class Personal(Base):
    __tablename__ = 'personal_info'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('profiles.id'), nullable=False)
    first_name = Column(String(255))
    last_name = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    gender = Column(String(20))
    date_of_birth = Column(String(50))
    
    # Relationship - CORREGIDO
    profile = relationship("Profile", back_populates="personal")

class Address(Base):
    __tablename__ = 'addresses'  # CONSISTENTE CON CONSULTAS
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('profiles.id'), nullable=False)
    street = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    postal_code = Column(String(20))
    
    # Relationship - CORREGIDO
    profile = relationship("Profile", back_populates="address")

class Professional(Base):
    __tablename__ = 'professional_info'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('profiles.id'), nullable=False)
    position = Column(String(255))
    company = Column(String(255))
    salary = Column(Float)
    department = Column(String(255))
    hire_date = Column(String(50))
    
    # Relationship - CORREGIDO
    profile = relationship("Profile", back_populates="professional")

class Bank(Base):
    __tablename__ = 'bank_info'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('profiles.id'), nullable=False)
    bank_name = Column(String(255))
    account_number = Column(String(100))
    routing_number = Column(String(50))
    
    # Relationship - CORREGIDO
    profile = relationship("Profile", back_populates="bank")

class Network(Base):
    __tablename__ = 'network_info'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('profiles.id'), nullable=False)
    ip_address = Column(String(50))
    mac_address = Column(String(100))
    domain = Column(String(255))
    
    # Relationship - CORREGIDO
    profile = relationship("Profile", back_populates="network")

# Database connection function
def get_mysql_connection():
    """Get MySQL connection using environment variables"""
    host = os.getenv('MYSQL_HOST', 'localhost')
    port = os.getenv('MYSQL_PORT', '3307')
    user = os.getenv('MYSQL_USER', 'hr_user')
    password = os.getenv('MYSQL_PASSWORD', 'hr_password')
    database = os.getenv('MYSQL_DATABASE', 'hr_analytics')
    
    connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    engine = create_engine(connection_string, echo=False)
    
    # Create tables
    Base.metadata.create_all(engine)
    
    return engine

# Initialize database when imported
try:
    engine = get_mysql_connection()
    SessionLocal = sessionmaker(bind=engine)
    print("✅ MySQL models initialized successfully")
except Exception as e:
    print(f"❌ Error initializing MySQL: {e}")
