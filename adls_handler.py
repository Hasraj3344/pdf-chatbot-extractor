"""
Simplified ADLS Handler with better error handling
"""
import logging
import json
import uuid
from datetime import datetime
import io

try:
    from azure.storage.filedatalake import DataLakeServiceClient
    from azure.core.credentials import AzureNamedKeyCredential
    AZURE_IMPORTS_OK = True
except ImportError as e:
    logging.error(f"Failed to import Azure libraries: {e}")
    AZURE_IMPORTS_OK = False

try:
    from config import Config
    CONFIG_IMPORT_OK = True
except Exception as e:
    logging.error(f"Failed to import Config: {e}")
    CONFIG_IMPORT_OK = False

class ADLSHandler:
    def __init__(self):
        if not AZURE_IMPORTS_OK:
            raise ImportError("Azure libraries not available. Please install azure-storage-file-datalake")
        
        if not CONFIG_IMPORT_OK:
            raise ImportError("Config module not available. Please check your config.py and .env files")
        
        try:
            self.config = Config()
            
            # Create credentials
            credential = AzureNamedKeyCredential(
                self.config.ADLS_ACCOUNT_NAME, 
                self.config.ADLS_ACCOUNT_KEY
            )
            
            # Initialize ADLS client
            self.service_client = DataLakeServiceClient(
                account_url=self.config.adls_account_url,
                credential=credential
            )
            
            self.filesystem_name = self.config.ADLS_FILESYSTEM_NAME
            self.filesystem_client = self.service_client.get_file_system_client(
                file_system=self.filesystem_name
            )
            
            # Initialize directory structure
            self._initialize_directories()
            
        except Exception as e:
            logging.error(f"Failed to initialize ADLS Handler: {str(e)}")
            raise Exception(f"ADLS configuration error: {str(e)}")
    
    def _initialize_directories(self):
        """Initialize the directory structure in ADLS"""
        try:
            # Create filesystem if it doesn't exist
            try:
                self.filesystem_client.create_file_system()
                logging.info(f"Created filesystem: {self.filesystem_name}")
            except Exception:
                logging.info(f"Filesystem {self.filesystem_name} already exists")
            
            # Create directories
            directories = [
                self.config.PDF_DIRECTORY,
                self.config.EXTRACTED_DATA_DIRECTORY,
                self.config.METADATA_DIRECTORY
            ]
            
            for directory in directories:
                try:
                    self.filesystem_client.create_directory(directory)
                    logging.info(f"Created directory: {directory}")
                except Exception:
                    logging.info(f"Directory {directory} already exists")
                    
        except Exception as e:
            logging.error(f"Error initializing directories: {str(e)}")
    
    def test_connection(self):
        """Test the ADLS connection"""
        try:
            # Try to get filesystem properties to test connection
            self.filesystem_client.get_file_system_properties()
            return True
        except Exception as e:
            logging.error(f"ADLS connection test failed: {str(e)}")
            return False
    
    def list_pdf_files(self):
        """List all PDF files in the PDF directory"""
        try:
            directory_client = self.filesystem_client.get_directory_client(
                self.config.PDF_DIRECTORY
            )
            
            pdf_files = []
            paths = directory_client.get_paths()
            
            for path in paths:
                if path.name.lower().endswith('.pdf') and not path.is_directory:
                    # Get file properties
                    file_client = self.filesystem_client.get_file_client(path.name)
                    properties = file_client.get_file_properties()
                    
                    pdf_files.append({
                        'name': path.name.split('/')[-1],  # Get just filename
                        'full_path': path.name,
                        'size': properties.size,
                        'last_modified': properties.last_modified
                    })
            
            return pdf_files
            
        except Exception as e:
            logging.error(f"Error listing PDF files: {str(e)}")
            return []
    
    def upload_pdf(self, file_name, file_content):
        """Upload PDF file to ADLS"""
        try:
            file_path = f"{self.config.PDF_DIRECTORY}/{file_name}"
            file_client = self.filesystem_client.get_file_client(file_path)
            
            # Upload file
            file_client.upload_data(
                file_content, 
                overwrite=True
            )
            
            logging.info(f"Uploaded PDF: {file_name}")
            return True
            
        except Exception as e:
            logging.error(f"Error uploading PDF {file_name}: {str(e)}")
            return False
    
    def download_pdf(self, file_name):
        """Download PDF file from ADLS"""
        try:
            file_path = f"{self.config.PDF_DIRECTORY}/{file_name}"
            file_client = self.filesystem_client.get_file_client(file_path)
            
            # Download file
            download_stream = file_client.download_file()
            return download_stream.readall()
            
        except Exception as e:
            logging.error(f"Error downloading PDF {file_name}: {str(e)}")
            return None
    
    def save_extracted_data(self, file_name, e_file_id, personal_info):
        """Save extracted personal information as JSON"""
        try:
            # Prepare data structure
            data = {
                'e_file_id': e_file_id,
                'source_file': file_name,
                'extracted_info': personal_info,
                'extraction_timestamp': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            # Save as JSON file
            json_file_name = f"{e_file_id}.json"
            file_path = f"{self.config.EXTRACTED_DATA_DIRECTORY}/{json_file_name}"
            
            file_client = self.filesystem_client.get_file_client(file_path)
            
            # Convert to JSON string
            json_data = json.dumps(data, indent=2, default=str)
            
            # Upload JSON data
            file_client.upload_data(
                json_data, 
                overwrite=True
            )
            
            # Also create/update an index file for searching
            self._update_search_index(e_file_id, personal_info, file_name)
            
            logging.info(f"Saved extracted data for: {file_name}")
            return True
            
        except Exception as e:
            logging.error(f"Error saving extracted data for {file_name}: {str(e)}")
            return False
    
    def _update_search_index(self, e_file_id, personal_info, file_name):
        """Update search index for quick lookups"""
        try:
            index_path = f"{self.config.METADATA_DIRECTORY}/search_index.json"
            file_client = self.filesystem_client.get_file_client(index_path)
            
            # Load existing index
            try:
                download_stream = file_client.download_file()
                existing_data = json.loads(download_stream.readall().decode('utf-8'))
            except:
                existing_data = {'records': []}
            
            # Create new record
            record = {
                'e_file_id': e_file_id,
                'file_name': file_name,
                'first_name': personal_info.get('first_name'),
                'last_name': personal_info.get('last_name'),
                'email': personal_info.get('email'),
                'phone_number': personal_info.get('phone_number'),
                'address': personal_info.get('address'),
                'date_of_birth': personal_info.get('date_of_birth'),
                'age': personal_info.get('age'),
                'document_type': personal_info.get('document_type'),
                'confidence_score': personal_info.get('confidence_score'),
                'created_date': datetime.now().isoformat()
            }
            
            # Remove any existing record with same e_file_id
            existing_data['records'] = [
                r for r in existing_data['records'] 
                if r.get('e_file_id') != e_file_id
            ]
            
            # Add new record
            existing_data['records'].append(record)
            
            # Save updated index
            json_data = json.dumps(existing_data, indent=2, default=str)
            file_client.upload_data(json_data, overwrite=True)
            
        except Exception as e:
            logging.error(f"Error updating search index: {str(e)}")
    
    def get_extracted_data(self, e_file_id):
        """Get extracted data by e-file ID"""
        try:
            file_path = f"{self.config.EXTRACTED_DATA_DIRECTORY}/{e_file_id}.json"
            file_client = self.filesystem_client.get_file_client(file_path)
            
            download_stream = file_client.download_file()
            data = json.loads(download_stream.readall().decode('utf-8'))
            
            return data
            
        except Exception as e:
            logging.error(f"Error getting extracted data for {e_file_id}: {str(e)}")
            return None
    
    def search_by_email(self, email):
        """Search records by email"""
        try:
            index_path = f"{self.config.METADATA_DIRECTORY}/search_index.json"
            file_client = self.filesystem_client.get_file_client(index_path)
            
            download_stream = file_client.download_file()
            index_data = json.loads(download_stream.readall().decode('utf-8'))
            
            # Search for matching emails
            results = []
            for record in index_data.get('records', []):
                if record.get('email') and email.lower() in record['email'].lower():
                    results.append(record)
            
            return results
            
        except Exception as e:
            logging.error(f"Error searching by email {email}: {str(e)}")
            return []
    
    def search_by_name(self, name):
        """Search records by name"""
        try:
            index_path = f"{self.config.METADATA_DIRECTORY}/search_index.json"
            file_client = self.filesystem_client.get_file_client(index_path)
            
            download_stream = file_client.download_file()
            index_data = json.loads(download_stream.readall().decode('utf-8'))
            
            # Search for matching names
            results = []
            name_lower = name.lower()
            
            for record in index_data.get('records', []):
                first_name = (record.get('first_name') or '').lower()
                last_name = (record.get('last_name') or '').lower()
                full_name = f"{first_name} {last_name}".strip()
                
                if (name_lower in first_name or 
                    name_lower in last_name or 
                    name_lower in full_name):
                    results.append(record)
            
            return results
            
        except Exception as e:
            logging.error(f"Error searching by name {name}: {str(e)}")
            return []
    
    def get_all_records(self, limit=100):
        """Get all records from search index"""
        try:
            index_path = f"{self.config.METADATA_DIRECTORY}/search_index.json"
            file_client = self.filesystem_client.get_file_client(index_path)
            
            download_stream = file_client.download_file()
            index_data = json.loads(download_stream.readall().decode('utf-8'))
            
            # Sort by created_date descending and limit
            records = index_data.get('records', [])
            records.sort(key=lambda x: x.get('created_date', ''), reverse=True)
            
            return records[:limit]
            
        except Exception as e:
            logging.error(f"Error getting all records: {str(e)}")
            return []
    
    def update_extracted_data(self, e_file_id, updated_info):
        """Update extracted data"""
        try:
            # Get existing data
            existing_data = self.get_extracted_data(e_file_id)
            if not existing_data:
                return False
            
            # Update the extracted info
            existing_data['extracted_info'].update(updated_info)
            existing_data['last_updated'] = datetime.now().isoformat()
            
            # Save updated data
            file_path = f"{self.config.EXTRACTED_DATA_DIRECTORY}/{e_file_id}.json"
            file_client = self.filesystem_client.get_file_client(file_path)
            
            json_data = json.dumps(existing_data, indent=2, default=str)
            file_client.upload_data(json_data, overwrite=True)
            
            # Update search index
            self._update_search_index(e_file_id, existing_data['extracted_info'], existing_data['source_file'])
            
            return True
            
        except Exception as e:
            logging.error(f"Error updating extracted data for {e_file_id}: {str(e)}")
            return False
    
    def delete_record(self, e_file_id):
        """Delete a record and its associated data"""
        try:
            # Delete extracted data file
            data_path = f"{self.config.EXTRACTED_DATA_DIRECTORY}/{e_file_id}.json"
            data_file_client = self.filesystem_client.get_file_client(data_path)
            data_file_client.delete_file()
            
            # Update search index to remove the record
            index_path = f"{self.config.METADATA_DIRECTORY}/search_index.json"
            file_client = self.filesystem_client.get_file_client(index_path)
            
            download_stream = file_client.download_file()
            index_data = json.loads(download_stream.readall().decode('utf-8'))
            
            # Remove record from index
            index_data['records'] = [
                r for r in index_data['records'] 
                if r.get('e_file_id') != e_file_id
            ]
            
            # Save updated index
            json_data = json.dumps(index_data, indent=2, default=str)
            file_client.upload_data(json_data, overwrite=True)
            
            return True
            
        except Exception as e:
            logging.error(f"Error deleting record {e_file_id}: {str(e)}")
            return False