import pyodbc
import logging
from config import Config
import uuid
from datetime import datetime

class DatabaseHandler:
    def __init__(self):
        self.config = Config()
        self.connection_string = self.config.sql_connection_string
    
    def get_connection(self):
        """Get database connection"""
        try:
            connection = pyodbc.connect(self.connection_string)
            return connection
        except Exception as e:
            logging.error(f"Error connecting to database: {str(e)}")
            return None
    
    def insert_personal_info(self, file_name, personal_info):
        """Insert extracted personal information into database"""
        try:
            connection = self.get_connection()
            if not connection:
                return False
            
            cursor = connection.cursor()
            
            # Generate unique e-file ID
            e_file_id = str(uuid.uuid4())
            
            # Prepare SQL query
            sql = """
            INSERT INTO PersonalInformation 
            (e_file_id, file_name, first_name, last_name, email, phone_number, 
             address, date_of_birth, document_type, extracted_text, confidence_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            # Prepare values
            values = (
                e_file_id,
                file_name,
                personal_info.get('first_name'),
                personal_info.get('last_name'),
                personal_info.get('email'),
                personal_info.get('phone_number'),
                personal_info.get('address'),
                personal_info.get('date_of_birth'),
                personal_info.get('document_type'),
                personal_info.get('extracted_text'),
                personal_info.get('confidence_score', 0.0)
            )
            
            cursor.execute(sql, values)
            connection.commit()
            
            cursor.close()
            connection.close()
            
            return e_file_id
            
        except Exception as e:
            logging.error(f"Error inserting personal info: {str(e)}")
            return None
    
    def get_personal_info_by_efile_id(self, e_file_id):
        """Retrieve personal information by e-file ID"""
        try:
            connection = self.get_connection()
            if not connection:
                return None
            
            cursor = connection.cursor()
            
            sql = """
            SELECT * FROM PersonalInformation 
            WHERE e_file_id = ?
            """
            
            cursor.execute(sql, (e_file_id,))
            row = cursor.fetchone()
            
            if row:
                columns = [column[0] for column in cursor.description]
                result = dict(zip(columns, row))
                
                cursor.close()
                connection.close()
                return result
            
            cursor.close()
            connection.close()
            return None
            
        except Exception as e:
            logging.error(f"Error retrieving personal info: {str(e)}")
            return None
    
    def search_by_email(self, email):
        """Search personal information by email"""
        try:
            connection = self.get_connection()
            if not connection:
                return []
            
            cursor = connection.cursor()
            
            sql = """
            SELECT e_file_id, file_name, first_name, last_name, email, 
                   phone_number, document_type, created_date
            FROM PersonalInformation 
            WHERE email LIKE ?
            """
            
            cursor.execute(sql, (f'%{email}%',))
            rows = cursor.fetchall()
            
            results = []
            if rows:
                columns = [column[0] for column in cursor.description]
                for row in rows:
                    results.append(dict(zip(columns, row)))
            
            cursor.close()
            connection.close()
            return results
            
        except Exception as e:
            logging.error(f"Error searching by email: {str(e)}")
            return []
    
    def get_all_records(self, limit=100):
        """Get all records with pagination"""
        try:
            connection = self.get_connection()
            if not connection:
                return []
            
            cursor = connection.cursor()
            
            sql = f"""
            SELECT TOP {limit} e_file_id, file_name, first_name, last_name, 
                   email, phone_number, document_type, created_date, confidence_score
            FROM PersonalInformation 
            ORDER BY created_date DESC
            """
            
            cursor.execute(sql)
            rows = cursor.fetchall()
            
            results = []
            if rows:
                columns = [column[0] for column in cursor.description]
                for row in rows:
                    results.append(dict(zip(columns, row)))
            
            cursor.close()
            connection.close()
            return results
            
        except Exception as e:
            logging.error(f"Error getting all records: {str(e)}")
            return []
    
    def update_personal_info(self, e_file_id, updated_info):
        """Update personal information"""
        try:
            connection = self.get_connection()
            if not connection:
                return False
            
            cursor = connection.cursor()
            
            sql = """
            UPDATE PersonalInformation 
            SET first_name = ?, last_name = ?, email = ?, phone_number = ?, 
                address = ?, date_of_birth = ?, document_type = ?, updated_date = ?
            WHERE e_file_id = ?
            """
            
            values = (
                updated_info.get('first_name'),
                updated_info.get('last_name'),
                updated_info.get('email'),
                updated_info.get('phone_number'),
                updated_info.get('address'),
                updated_info.get('date_of_birth'),
                updated_info.get('document_type'),
                datetime.now(),
                e_file_id
            )
            
            cursor.execute(sql, values)
            connection.commit()
            
            cursor.close()
            connection.close()
            return True
            
        except Exception as e:
            logging.error(f"Error updating personal info: {str(e)}")
            return False