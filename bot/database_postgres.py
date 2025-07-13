import logging
import psycopg2
import os
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class PostgreSQLDatabase:
    """PostgreSQL database management for TeleFeed bot"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        self.connection = None
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        try:
            self.connection = psycopg2.connect(self.database_url)
            cursor = self.connection.cursor()
            
            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_licenses (
                    user_id BIGINT PRIMARY KEY,
                    license_code VARCHAR(255) NOT NULL,
                    validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    active BOOLEAN DEFAULT TRUE
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_connections (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    phone_number VARCHAR(20) NOT NULL,
                    connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    active BOOLEAN DEFAULT TRUE,
                    UNIQUE(user_id, phone_number)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS redirections (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    phone_number VARCHAR(20) NOT NULL,
                    source_chat_id BIGINT NOT NULL,
                    destination_chat_id BIGINT NOT NULL,
                    active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transformations (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    phone_number VARCHAR(20) NOT NULL,
                    transformation_type VARCHAR(50) NOT NULL,
                    settings JSON,
                    active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS whitelist_filters (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    phone_number VARCHAR(20) NOT NULL,
                    filter_name VARCHAR(100) NOT NULL,
                    filter_value TEXT NOT NULL,
                    active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS blacklist_filters (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    phone_number VARCHAR(20) NOT NULL,
                    filter_name VARCHAR(100) NOT NULL,
                    filter_value TEXT NOT NULL,
                    active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    phone_number VARCHAR(20) NOT NULL,
                    session_file VARCHAR(255) NOT NULL,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    active BOOLEAN DEFAULT TRUE,
                    UNIQUE(user_id, phone_number)
                )
            ''')
            
            self.connection.commit()
            cursor.close()
            logger.info("✅ Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            if self.connection:
                self.connection.rollback()
    
    def store_license(self, user_id, license_code):
        """Store validated license"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO user_licenses (user_id, license_code, validated_at, active)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE SET
                    license_code = EXCLUDED.license_code,
                    validated_at = EXCLUDED.validated_at,
                    active = EXCLUDED.active
            ''', (user_id, license_code, datetime.now(), True))
            self.connection.commit()
            cursor.close()
            logger.info(f"License stored for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error storing license: {e}")
            self.connection.rollback()
            return False
    
    def is_user_licensed(self, user_id):
        """Check if user has valid license"""
        try:
            # Check if user is admin (owner always has access)
            admin_id = os.getenv("ADMIN_ID")
            if admin_id and str(user_id) == admin_id:
                return True
            
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT active FROM user_licenses WHERE user_id = %s
            ''', (user_id,))
            result = cursor.fetchone()
            cursor.close()
            
            return result and result[0] if result else False
        except Exception as e:
            logger.error(f"Error checking license: {e}")
            return False
    
    def store_connection(self, user_id, phone_number):
        """Store successful phone connection"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO user_connections (user_id, phone_number, connected_at, active)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id, phone_number) DO UPDATE SET
                    connected_at = EXCLUDED.connected_at,
                    active = EXCLUDED.active
            ''', (user_id, phone_number, datetime.now(), True))
            self.connection.commit()
            cursor.close()
            logger.info(f"Connection stored for user {user_id}, phone {phone_number}")
            return True
        except Exception as e:
            logger.error(f"Error storing connection: {e}")
            self.connection.rollback()
            return False
    
    def get_user_connections(self, user_id):
        """Get user's connected phone numbers"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT phone_number FROM user_connections 
                WHERE user_id = %s AND active = TRUE
            ''', (user_id,))
            results = cursor.fetchall()
            cursor.close()
            return [row[0] for row in results]
        except Exception as e:
            logger.error(f"Error getting connections: {e}")
            return []
    
    def store_redirection(self, user_id, phone_number, source_chat_id, destination_chat_id):
        """Store redirection configuration"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO redirections (user_id, phone_number, source_chat_id, destination_chat_id, active)
                VALUES (%s, %s, %s, %s, %s)
            ''', (user_id, phone_number, source_chat_id, destination_chat_id, True))
            self.connection.commit()
            cursor.close()
            logger.info(f"Redirection stored for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error storing redirection: {e}")
            self.connection.rollback()
            return False
    
    def get_user_redirections(self, user_id):
        """Get user's active redirections"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT phone_number, source_chat_id, destination_chat_id 
                FROM redirections 
                WHERE user_id = %s AND active = TRUE
            ''', (user_id,))
            results = cursor.fetchall()
            cursor.close()
            return [{"phone": row[0], "source": row[1], "destination": row[2]} for row in results]
        except Exception as e:
            logger.error(f"Error getting redirections: {e}")
            return []
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()

# Global database instance
db = PostgreSQLDatabase()