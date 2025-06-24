from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from kafka_consumer.db_clients.mysql_init import Base, Profile, Personal, Address, Professional, Bank, Network
import logging
import os
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MySQLClient:
    def __init__(self):
        """Initialize MySQL client"""
        try:
            # Get connection details from environment
            host = os.getenv('MYSQL_HOST', 'localhost')
            port = os.getenv('MYSQL_PORT', '3307')
            user = os.getenv('MYSQL_USER', 'hr_user')
            password = os.getenv('MYSQL_PASSWORD', 'hr_password')
            database = os.getenv('MYSQL_DATABASE', 'hr_analytics')
            
            # Create connection string
            connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
            
            # Create engine
            self.engine = create_engine(connection_string, echo=False)
            
            # Create tables if they don't exist
            Base.metadata.create_all(self.engine)
            
            # Create session
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            
            logger.info("✅ MySQL connection established successfully")
            
        except Exception as e:
            logger.error(f"❌ Error connecting to MySQL: {e}")
            raise

    def store_transformed(self, data: Dict[str, Any]) -> bool:
        """Store transformed employee data to MySQL"""
        try:
            # Extract employee ID
            employee_id = data.get('id') or data.get('employee_id')
            if not employee_id:
                logger.error("❌ No employee ID found in data")
                return False

            # Check if employee already exists
            existing_profile = self.session.query(Profile).filter_by(employee_id=employee_id).first()
            if existing_profile:
                logger.info(f"⚠️ Employee {employee_id} already exists, updating...")
                return self._update_employee(existing_profile, data)
            else:
                logger.info(f"➕ Creating new employee {employee_id}")
                return self._create_employee(data)

        except Exception as e:
            logger.error(f"❌ Error storing data to MySQL: {e}")
            self.session.rollback()
            return False

    def _create_employee(self, data: Dict[str, Any]) -> bool:
        """Create new employee record"""
        try:
            # Create Profile
            profile = Profile(
                employee_id=data.get('id') or data.get('employee_id'),
                name=f"{data.get('personal', {}).get('first_name', '')} {data.get('personal', {}).get('last_name', '')}".strip(),
                email=data.get('personal', {}).get('email'),
                created_at=data.get('created_at')
            )
            self.session.add(profile)
            self.session.flush()  # Get the ID

            # Create Personal info
            if 'personal' in data:
                personal = Personal(
                    profile_id=profile.id,
                    first_name=data['personal'].get('first_name'),
                    last_name=data['personal'].get('last_name'),
                    email=data['personal'].get('email'),
                    phone=data['personal'].get('phone'),
                    gender=data['personal'].get('gender'),
                    date_of_birth=data['personal'].get('date_of_birth')
                )
                self.session.add(personal)

            # Create Address info
            if 'location' in data:
                address = Address(
                    profile_id=profile.id,
                    street=data['location'].get('street'),
                    city=data['location'].get('city'),
                    state=data['location'].get('state'),
                    country=data['location'].get('country'),
                    postal_code=data['location'].get('postcode')
                )
                self.session.add(address)

            # Create Professional info
            if 'professional' in data:
                professional = Professional(
                    profile_id=profile.id,
                    position=data['professional'].get('position'),
                    company=data['professional'].get('company'),
                    salary=float(data['professional'].get('salary', 0)) if data['professional'].get('salary') else None,
                    department=data['professional'].get('department'),
                    hire_date=data['professional'].get('hire_date')
                )
                self.session.add(professional)

            # Create Bank info
            if 'bank' in data:
                bank = Bank(
                    profile_id=profile.id,
                    bank_name=data['bank'].get('bank_name'),
                    account_number=data['bank'].get('account_number'),
                    routing_number=data['bank'].get('routing_number')
                )
                self.session.add(bank)

            # Create Network info
            if 'net' in data:
                network = Network(
                    profile_id=profile.id,
                    ip_address=data['net'].get('ip_address'),
                    mac_address=data['net'].get('mac_address'),
                    domain=data['net'].get('domain')
                )
                self.session.add(network)

            # Commit all changes
            self.session.commit()
            logger.info(f"✅ Successfully created employee {profile.employee_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Error creating employee: {e}")
            self.session.rollback()
            return False

    def _update_employee(self, profile: Profile, data: Dict[str, Any]) -> bool:
        """Update existing employee record"""
        try:
            # Update profile
            profile.name = f"{data.get('personal', {}).get('first_name', '')} {data.get('personal', {}).get('last_name', '')}".strip()
            profile.email = data.get('personal', {}).get('email')

            # Update related records (simplified - you can expand this)
            if 'professional' in data:
                professional = self.session.query(Professional).filter_by(profile_id=profile.id).first()
                if professional:
                    professional.salary = float(data['professional'].get('salary', 0)) if data['professional'].get('salary') else professional.salary
                    professional.position = data['professional'].get('position', professional.position)
                    professional.company = data['professional'].get('company', professional.company)

            self.session.commit()
            logger.info(f"✅ Successfully updated employee {profile.employee_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Error updating employee: {e}")
            self.session.rollback()
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get basic statistics"""
        try:
            total_employees = self.session.query(Profile).count()
            
            # Get average salary
            avg_salary_result = self.session.query(text("AVG(salary) as avg_salary")).select_from(text("professional_info")).scalar()
            avg_salary = float(avg_salary_result) if avg_salary_result else 0

            return {
                'total_employees': total_employees,
                'avg_salary': round(avg_salary, 2)
            }

        except Exception as e:
            logger.error(f"❌ Error getting stats: {e}")
            return {'total_employees': 0, 'avg_salary': 0}

    def close(self):
        """Close the session"""
        if self.session:
            self.session.close()

# Create global instance
mysql_client = MySQLClient()

def store_transformed(data: Dict[str, Any]) -> bool:
    """Public function to store data"""
    return mysql_client.store_transformed(data)

def get_connection():
    """Get MySQL connection for FastAPI"""
    return mysql_client