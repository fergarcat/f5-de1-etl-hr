from sqlalchemy import ( 
    create_engine, text,
    Column,
    Integer,
    String,
    DECIMAL,
    ForeignKey,
    DateTime,
    Boolean,
    func,
)
from sqlalchemy.orm import declarative_base, relationship
from dotenv import load_dotenv
import os

# 1. Load environment variables
load_dotenv()
mysql_user = os.getenv('MYSQL_USER')
mysql_password = os.getenv('MYSQL_PASSWORD')
mysql_host = os.getenv('MYSQL_HOST')
mysql_database = os.getenv('MYSQL_DATABASE')


# 2. Create connection without specifying the database
mysql_uri_no_db = f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/"
engine_no_db = create_engine(mysql_uri_no_db, echo=True)

# 3. Create the database if it does not exist
with engine_no_db.connect() as conn:
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {mysql_database}"))
    conn.commit()


# 4. Create the connection engine with the database
mysql_uri = f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_database}"
engine = create_engine(mysql_uri, echo=True)

# 5. Declare base and models
Base = declarative_base()


class Profile(Base):
    __tablename__ = 'profile'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    passport = Column(String(25), nullable=False)
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime, onupdate=func.now())

    personal = relationship("Personal", back_populates="profile", uselist=False)
    address = relationship("Address", back_populates="profile", uselist=False)
    professional = relationship("Professional", back_populates="profile", uselist=False)
    bank = relationship("Bank", back_populates="profile", uselist=False)
    net = relationship("Net", back_populates="profile", uselist=False)


class Personal(Base):
    __tablename__ = 'personal_info'

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('profile.id'))
    email = Column(String(320), nullable=True)
    telfcountrycode = Column(String(5), nullable=True)
    telfnumber = Column(String(15), nullable=True)
    sex = Column(String(10), nullable=True)
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime, onupdate=func.now())

    profile = relationship("Profile", back_populates="personal")  


class Address(Base):
    __tablename__ = 'address'

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('profile.id'))
    address = Column(String(255))
    city = Column(String(100))
    postal_code = Column(String(20))
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime, onupdate=func.now())

    profile = relationship("Profile", back_populates="address")  


class Professional(Base):
    __tablename__ = 'professional_info'

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('profile.id'))
    company = Column(String(255))
    job = Column(String(100))
    company_email = Column(String(255))
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime, onupdate=func.now())

    profile = relationship("Profile", back_populates="professional")  


class Bank(Base):
    __tablename__ = 'payroll_info'

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('profile.id'))
    IBAN = Column(String(34), nullable=False)
    salary = Column(DECIMAL(12, 2))
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime, onupdate=func.now())

    profile = relationship("Profile", back_populates="bank") 


class Net(Base):
    __tablename__ = 'network_info'

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('profile.id'))
    IPv4 = Column(String(15), nullable=False)
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime, onupdate=func.now())

    profile = relationship("Profile", back_populates="net")  


# 6. Create tables if they do not exist
try:
    Base.metadata.drop_all(engine) 
    Base.metadata.create_all(engine)
    print("✅ Tables created successfully.")
except Exception as e:
    print(f"❌ Error creating tables: {e}")
