import json
import logging
from kafka import KafkaConsumer
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# Now import our modules
from kafka_consumer.db_clients import mongo, redis, sql
from kafka_consumer.etl import transform_data
from config.logger_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

class HRETLConsumer:
    def __init__(self):
        """Initialize Kafka consumer and database connections"""
        self.setup_kafka_consumer()
        self.mongo_client = mongo.mongo_client
        self.redis_client = redis.redis_client
        self.sql_client = sql.mysql_client
        
        logger.info("✅ HR ETL Consumer initialized successfully")

    def setup_kafka_consumer(self):
        """Setup Kafka consumer with environment variables"""
        try:
            kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
            topic = os.getenv('KAFKA_TOPIC', 'hr-employee-data')
            group_id = os.getenv('KAFKA_GROUP_ID', 'hr-etl-consumer')
            
            self.consumer = KafkaConsumer(
                topic,
                bootstrap_servers=[kafka_servers],
                group_id=group_id,
                auto_offset_reset='latest',
                enable_auto_commit=True,
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                consumer_timeout_ms=10000
            )
            
            logger.info(f"✅ Kafka consumer connected to {kafka_servers}, topic: {topic}")
            
        except Exception as e:
            logger.error(f"❌ Error setting up Kafka consumer: {e}")
            raise

    def process_message(self, message_value):
        """Process individual Kafka message"""
        try:
            logger.info(f"📨 Processing message: {message_value.get('id', 'unknown')}")
            
            # 1. Store raw data in MongoDB (for audit)
            mongo_result = self.store_raw_data(message_value)
            
            # 2. Transform data
            transformed_data = transform_data(message_value)
            if not transformed_data:
                logger.error("❌ Data transformation failed")
                return False
            
            # 3. Store transformed data in MySQL
            sql_result = sql.store_transformed(transformed_data)
            
            # 4. Update cache in Redis
            redis_result = self.update_cache(transformed_data)
            
            # Log results
            logger.info(f"📊 Processing results - MongoDB: {mongo_result}, MySQL: {sql_result}, Redis: {redis_result}")
            
            return sql_result
            
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
            return False

    def store_raw_data(self, data):
        """Store raw data in MongoDB"""
        try:
            # Add timestamp
            data['processed_at'] = datetime.utcnow().isoformat()
            
            # Store in MongoDB
            result = self.mongo_client.store_raw_employee(data)
            logger.info(f"✅ Raw data stored in MongoDB: {result}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error storing raw data: {e}")
            return False

    def update_cache(self, data):
        """Update Redis cache"""
        try:
            employee_id = data.get('id') or data.get('employee_id')
            if employee_id:
                cache_key = f"employee:{employee_id}"
                result = self.redis_client.set_employee_cache(cache_key, data)
                logger.info(f"✅ Cache updated for employee {employee_id}")
                return result
            return False
            
        except Exception as e:
            logger.error(f"❌ Error updating cache: {e}")
            return False

    def run(self):
        """Main consumer loop"""
        logger.info("🚀 Starting HR ETL Consumer...")
        logger.info("⏳ Waiting for messages...")
        
        try:
            for message in self.consumer:
                self.process_message(message.value)
                
        except KeyboardInterrupt:
            logger.info("🛑 Consumer stopped by user")
        except Exception as e:
            logger.error(f"❌ Consumer error: {e}")
        finally:
            self.consumer.close()
            logger.info("🔚 Consumer closed")

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Start consumer
    consumer = HRETLConsumer()
    consumer.run()
