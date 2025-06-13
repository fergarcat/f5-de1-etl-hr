import argparse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, relationship
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
mysql_user = os.getenv('MYSQL_USER')
mysql_password = os.getenv('MYSQL_PASSWORD')
mysql_host = os.getenv('MYSQL_HOST')
mysql_database = os.getenv('MYSQL_DATABASE')

# Parse command line arguments
parser = argparse.ArgumentParser(description="Initialize MySQL database and tables.")
parser.add_argument('--debug', action='store_true', help="Enable debug mode (echo=True in SQLAlchemy engine).")
parser.add_argument('--drop', action='store_true', help="Drop existing tables before creating new ones.")
args = parser.parse_args()

# Create engine without specifying database (for DB creation)
engine_no_db = create_engine(
    f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/",
    echo=args.debug
)

# Create the database if it doesn't exist
with engine_no_db.connect() as conn:
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {mysql_database}"))
    conn.commit()

# Create engine connected to the specific database
engine = create_engine(
    f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_database}",
    echo=args.debug
)

Base = declarative_base()

# ... aquí tus modelos ...


def main():
    try:
        if args.drop:
            print("Dropping existing tables...")
            Base.metadata.drop_all(engine)
            print("✅ Existing tables dropped successfully.")
        Base.metadata.create_all(engine)
        print("✅ Tables created successfully.")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")


if __name__ == "__main__":
    main()
