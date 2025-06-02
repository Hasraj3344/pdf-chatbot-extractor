from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from config import Config
import logging
import re
from datetime import datetime

class DocumentIntelligenceHandler:
    def __init__(self):
        self.config = Config()
        self.client = DocumentAnalysisClient(
            endpoint=self.config.DOCUMENT_INTELLIGENCE_ENDPOINT,
            credential=AzureKeyCredential(self.config.DOCUMENT_INTELLIGENCE_KEY)
        )
    
    def extract_personal_info(self, pdf_content):
        """Extract personal information from PDF using Document Intelligence"""
        try:
            # Analyze document using prebuilt-document model
            poller = self.client.begin_analyze_document(
                "prebuilt-document", 
                pdf_content
            )
            result = poller.result()
            
            # Extract text content
            extracted_text = ""
            for page in result.pages:
                for line in page.lines:
                    extracted_text += line.content + "\n"
            
            # Extract personal information using patterns and AI
            personal_info = self._extract_patterns(extracted_text)
            personal_info['extracted_text'] = extracted_text
            personal_info['confidence_score'] = self._calculate_confidence(result)
            
            return personal_info
            
        except Exception as e:
            logging.error(f"Error extracting personal info: {str(e)}")
            return None
    
    def _extract_patterns(self, text):
        """Extract personal information using regex patterns"""
        personal_info = {
            'first_name': None,
            'last_name': None,
            'email': None,
            'phone_number': None,
            'address': None,
            'date_of_birth': None,
            'age': None,
            'document_type': None
        }
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            personal_info['email'] = email_match.group()
        
        # Phone pattern (various formats)
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            personal_info['phone_number'] = phone_match.group()
        
        # Age pattern - Extract age and convert to date of birth
        age_patterns = [
            r'Age[:\s]+(\d{1,3})',
            r'age[:\s]+(\d{1,3})',
            r'AGE[:\s]+(\d{1,3})',
            r'(\d{1,3})\s+years?\s+old',
            r'(\d{1,3})\s+yrs?\s+old',
            r'Born[:\s]+(\d{1,3})\s+years?\s+ago'
        ]
        
        age = None
        for pattern in age_patterns:
            age_match = re.search(pattern, text, re.IGNORECASE)
            if age_match:
                try:
                    age = int(age_match.group(1))
                    if 0 <= age <= 150:  # Reasonable age range
                        personal_info['age'] = age
                        # Calculate date of birth from age
                        current_date = datetime.now()
                        birth_year = current_date.year - age
                        # Assume birth date is January 1st if no specific date given
                        date_of_birth = f"{birth_year}-01-01"
                        personal_info['date_of_birth'] = date_of_birth
                        break
                except ValueError:
                    continue
        
        # Date patterns (MM/DD/YYYY, DD/MM/YYYY, YYYY-MM-DD) - if no age found
        if not personal_info['date_of_birth']:
            date_patterns = [
                r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b',
                r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b'
            ]
            for pattern in date_patterns:
                date_match = re.search(pattern, text)
                if date_match:
                    try:
                        # Try to parse the date
                        date_str = date_match.group()
                        # Convert to standard format YYYY-MM-DD
                        if '/' in date_str:
                            parts = date_str.split('/')
                        else:
                            parts = date_str.split('-')
                        
                        if len(parts) == 3:
                            # Try different date formats
                            if len(parts[0]) == 4:  # YYYY-MM-DD or YYYY/MM/DD
                                formatted_date = f"{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
                            elif len(parts[2]) == 4:  # MM/DD/YYYY or DD/MM/YYYY
                                # Assume MM/DD/YYYY format
                                formatted_date = f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
                            else:
                                continue
                            
                            personal_info['date_of_birth'] = formatted_date
                            
                            # Calculate age from date of birth
                            try:
                                birth_date = datetime.strptime(formatted_date, '%Y-%m-%d')
                                today = datetime.now()
                                calculated_age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                                if 0 <= calculated_age <= 150:
                                    personal_info['age'] = calculated_age
                            except:
                                pass
                            break
                    except:
                        continue
        
        # Name extraction (simple approach - look for common patterns)
        name_patterns = [
            r'Name[:\s]+([A-Za-z\s]+)',
            r'Full Name[:\s]+([A-Za-z\s]+)',
            r'First Name[:\s]+([A-Za-z]+)',
            r'Last Name[:\s]+([A-Za-z]+)'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if 'First Name' in pattern:
                    personal_info['first_name'] = match.group(1).strip()
                elif 'Last Name' in pattern:
                    personal_info['last_name'] = match.group(1).strip()
                else:
                    # Split full name
                    full_name = match.group(1).strip().split()
                    if len(full_name) >= 2:
                        personal_info['first_name'] = full_name[0]
                        personal_info['last_name'] = ' '.join(full_name[1:])
                    elif len(full_name) == 1:
                        personal_info['first_name'] = full_name[0]
        
        # Address pattern (basic)
        address_pattern = r'Address[:\s]+([A-Za-z0-9\s,.-]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr)[A-Za-z0-9\s,.-]*)'
        address_match = re.search(address_pattern, text, re.IGNORECASE)
        if address_match:
            personal_info['address'] = address_match.group(1).strip()
        
        # Document type detection
        doc_types = ['passport', 'driver license', 'id card', 'birth certificate', 'resume', 'cv']
        text_lower = text.lower()
        for doc_type in doc_types:
            if doc_type in text_lower:
                personal_info['document_type'] = doc_type.title()
                break
        
        return personal_info
    
    def _calculate_confidence(self, result):
        """Calculate overall confidence score"""
        total_confidence = 0
        element_count = 0
        
        for page in result.pages:
            for line in page.lines:
                if hasattr(line, 'confidence'):
                    total_confidence += line.confidence
                    element_count += 1
        
        if element_count > 0:
            return total_confidence / element_count
        return 0.0