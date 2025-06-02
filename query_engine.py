import json
import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
import pandas as pd

# OpenAI imports with error handling
try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI not available. Using basic pattern matching only.")

from config import Config

class QueryEngine:
    """
    Enhanced query engine that uses OpenAI for intelligent query interpretation
    """
    
    def __init__(self, adls_handler):
        self.adls_handler = adls_handler
        self.config = Config()
        self.query_patterns = self._initialize_patterns()
        
        # Initialize OpenAI client
        self.openai_client = None
        self.use_ai = False
        
        if OPENAI_AVAILABLE:
            self._initialize_openai()
    
    def _initialize_openai(self):
        """Initialize OpenAI client"""
        try:
            if self.config.use_openai:
                self.openai_client = OpenAI(api_key=self.config.OPENAI_API_KEY)
                self.use_ai = True
                logging.info("✅ OpenAI client initialized successfully")
            elif self.config.use_azure_openai:
                self.openai_client = OpenAI(
                    api_key=self.config.AZURE_OPENAI_API_KEY,
                    base_url=f"{self.config.AZURE_OPENAI_ENDPOINT}/openai/deployments/{self.config.AZURE_OPENAI_DEPLOYMENT_NAME}"
                )
                self.use_ai = True
                logging.info("✅ Azure OpenAI client initialized successfully")
            else:
                logging.info("ℹ️  No OpenAI configuration found. Using pattern matching.")
        except Exception as e:
            logging.error(f"Failed to initialize OpenAI: {str(e)}")
            self.use_ai = False
    
    def _initialize_patterns(self):
        """Initialize regex patterns for different types of queries"""
        return {
            'count_files': [
                r'how many (files|pdfs|documents) (are there|processed|uploaded)',
                r'(total|count of) (files|pdfs|documents)',
                r'number of (files|pdfs|documents)',
                r'count (files|pdfs|documents)'
            ],
            'count_people': [
                r'how many (people|persons|individuals|employees|users)',
                r'(total|count of) (people|persons|individuals|employees|users)',
                r'number of (people|persons|individuals|employees|users)',
                r'count (people|persons|individuals|employees|users)'
            ],
            'search_by_name': [
                r'find (.*?) (person|people|individual)',
                r'search for (.*?) (person|people|individual)',
                r'who is (.*?)[\?]?',
                r'show me (.*?) (details|information|info)'
            ],
            'search_by_email': [
                r'find email (.*?)[\?]?',
                r'search for email (.*?)[\?]?',
                r'who has email (.*?)[\?]?',
                r'email (.*?)[\?]?'
            ],
            'recent_files': [
                r'recent (files|pdfs|documents)',
                r'latest (files|pdfs|documents)',
                r'(files|pdfs|documents) (today|yesterday|this week|last week)',
                r'show me recent (files|pdfs|documents)'
            ],
            'files_by_type': [
                r'what (kind|type|types) of (documents|files)',
                r'document (types|kinds)',
                r'what documents do (i|we) have',
                r'show me document types',
                r'list document types',
                r'how many (.*?) (documents|files)',
                r'(count|number) of (.*?) (documents|files)',
                r'show me (.*?) (documents|files)'
            ],
            'confidence_stats': [
                r'confidence (score|scores|statistics|stats)',
                r'accuracy (score|scores|statistics|stats)',
                r'extraction (quality|confidence)'
            ],
            'summary_stats': [
                r'(summary|statistics|stats|overview)',
                r'show me (summary|statistics|stats|overview)',
                r'give me (summary|statistics|stats|overview)'
            ]
        }
    
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """Process user query using AI or pattern matching"""
        user_query = user_query.lower().strip()
        
        try:
            # First try AI-powered interpretation
            if self.use_ai:
                ai_response = self._process_with_ai(user_query)
                if ai_response:
                    return ai_response
            
            # Fallback to pattern matching
            query_type, extracted_params = self._match_query_pattern(user_query)
            
            if query_type:
                return self._execute_query(query_type, extracted_params, user_query)
            else:
                return self._handle_unknown_query(user_query)
                
        except Exception as e:
            logging.error(f"Error processing query: {str(e)}")
            return {
                'success': False,
                'message': f"Sorry, I encountered an error processing your query: {str(e)}",
                'data': None
            }
    
    def _process_with_ai(self, user_query: str) -> Dict[str, Any]:
        """Process query using OpenAI for intelligent interpretation"""
        try:
            # Get current data context
            stats = self._get_data_context()
            
            system_prompt = f"""You are a helpful assistant for a PDF document processing system. 
            
Current data context:
- Total PDF files: {stats['total_pdf_files']}
- Processed files: {stats['total_processed_files']}
- Unique people: {stats['unique_people']}
- Document types: {list(stats.get('document_types', {}).keys())}

Available query types and their purposes:
- count_files: Count total files processed
- count_people: Count unique individuals 
- search_by_name: Find person by name (requires name parameter)
- search_by_email: Find person by email (requires email parameter)
- recent_files: Show recently processed files
- files_by_type: Show document types or filter by document type (use this for "what kind of documents" questions)
- confidence_stats: Show extraction confidence statistics
- summary_stats: Show overall system statistics

Special handling for document type queries:
- "what kind of documents" or "what types of documents" should use files_by_type
- "document types" should use files_by_type
- If no specific document type is mentioned, show all document types

Analyze the user's query and determine:
1. The most appropriate query_type from the list above
2. Any parameters needed (like name or email for searches)
3. A natural language response

Respond in JSON format:
{{
    "query_type": "appropriate_type_from_list",
    "parameters": {{"param_name": "value"}},
    "response": "Natural language response",
    "confidence": 0.9
}}

If the query doesn't match any type well, use query_type: "unknown"."""

            response = self.openai_client.chat.completions.create(
                model=self.config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            ai_result = json.loads(response.choices[0].message.content)
            
            # Execute the AI-determined query
            if ai_result.get('confidence', 0) > 0.5 and ai_result.get('query_type') != 'unknown':
                query_type = ai_result['query_type']
                params = ai_result.get('parameters', {})
                
                # Execute the query
                result = self._execute_ai_query(query_type, params, user_query)
                
                # Enhance response with AI-generated natural language
                if result.get('success'):
                    result['ai_enhanced'] = True
                    result['ai_response'] = ai_result.get('response', '')
                
                return result
            
            return None
            
        except Exception as e:
            logging.error(f"AI processing failed: {str(e)}")
            return None
    
    def _execute_ai_query(self, query_type: str, params: dict, original_query: str) -> Dict[str, Any]:
        """Execute AI-determined query"""
        
        if query_type == 'count_files':
            return self._count_files()
            
        elif query_type == 'count_people':
            return self._count_people()
            
        elif query_type == 'search_by_name':
            name = params.get('name', '')
            return self._search_by_name(name)
            
        elif query_type == 'search_by_email':
            email = params.get('email', '')
            return self._search_by_email(email)
            
        elif query_type == 'recent_files':
            return self._get_recent_files(original_query)
            
        elif query_type == 'files_by_type':
            doc_type = params.get('document_type', '')
            return self._get_files_by_type(doc_type)
            
        elif query_type == 'confidence_stats':
            return self._get_confidence_stats()
            
        elif query_type == 'summary_stats':
            return self._get_summary_stats()
            
        else:
            return self._handle_unknown_query(original_query)
    
    def _get_data_context(self) -> Dict[str, Any]:
        """Get current data context for AI"""
        try:
            records = self.adls_handler.get_all_records(limit=1000)
            pdf_files = self.adls_handler.list_pdf_files()
            
            # Count unique people
            unique_emails = set()
            doc_types = {}
            
            for record in records:
                email = record.get('email', '').lower().strip()
                if email:
                    unique_emails.add(email)
                
                doc_type = record.get('document_type', 'Unknown')
                doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
            
            return {
                'total_pdf_files': len(pdf_files),
                'total_processed_files': len(records),
                'unique_people': len(unique_emails),
                'document_types': doc_types
            }
        except:
            return {
                'total_pdf_files': 0,
                'total_processed_files': 0,
                'unique_people': 0,
                'document_types': {}
            }
    
    def _match_query_pattern(self, query: str):
        """Match user query against predefined patterns (fallback method)"""
        for query_type, patterns in self.query_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, query, re.IGNORECASE)
                if match:
                    return query_type, match.groups()
        return None, None
    
    def _execute_query(self, query_type: str, params: tuple, original_query: str) -> Dict[str, Any]:
        """Execute the matched query type (fallback method)"""
        
        if query_type == 'count_files':
            return self._count_files()
            
        elif query_type == 'count_people':
            return self._count_people()
            
        elif query_type == 'search_by_name':
            name = params[0] if params else ""
            return self._search_by_name(name)
            
        elif query_type == 'search_by_email':
            email = params[0] if params else ""
            return self._search_by_email(email)
            
        elif query_type == 'recent_files':
            return self._get_recent_files(original_query)
            
        elif query_type == 'files_by_type':
            doc_type = params[0] if params else ""
            return self._get_files_by_type(doc_type)
            
        elif query_type == 'confidence_stats':
            return self._get_confidence_stats()
            
        elif query_type == 'summary_stats':
            return self._get_summary_stats()
            
        else:
            return self._handle_unknown_query(original_query)
    
    def _count_files(self) -> Dict[str, Any]:
        """Count total number of processed files"""
        try:
            records = self.adls_handler.get_all_records(limit=1000)
            count = len(records)
            
            return {
                'success': True,
                'message': f"I found {count} processed files in the system.",
                'data': {
                    'total_files': count,
                    'query_type': 'count_files'
                }
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Sorry, I couldn't count the files: {str(e)}",
                'data': None
            }
    
    def _count_people(self) -> Dict[str, Any]:
        """Count unique people/individuals"""
        try:
            records = self.adls_handler.get_all_records(limit=1000)
            
            # Count unique people based on email or name combination
            unique_people = set()
            for record in records:
                email = record.get('email', '').lower().strip()
                first_name = (record.get('first_name', '') or '').lower().strip()
                last_name = (record.get('last_name', '') or '').lower().strip()
                
                if email:
                    unique_people.add(email)
                elif first_name and last_name:
                    unique_people.add(f"{first_name}_{last_name}")
                elif first_name:
                    unique_people.add(first_name)
            
            count = len(unique_people)
            
            return {
                'success': True,
                'message': f"I found {count} unique individuals in the system.",
                'data': {
                    'total_people': count,
                    'query_type': 'count_people'
                }
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Sorry, I couldn't count the people: {str(e)}",
                'data': None
            }
    
    def _search_by_name(self, name: str) -> Dict[str, Any]:
        """Search for people by name"""
        if not name.strip():
            return {
                'success': False,
                'message': "Please specify a name to search for.",
                'data': None
            }
        
        try:
            results = self.adls_handler.search_by_name(name.strip())
            
            if results:
                return {
                    'success': True,
                    'message': f"I found {len(results)} person(s) matching '{name}':",
                    'data': {
                        'results': results,
                        'query_type': 'search_by_name',
                        'search_term': name
                    }
                }
            else:
                return {
                    'success': True,
                    'message': f"No person found with the name '{name}'.",
                    'data': {
                        'results': [],
                        'query_type': 'search_by_name',
                        'search_term': name
                    }
                }
        except Exception as e:
            return {
                'success': False,
                'message': f"Sorry, I couldn't search for '{name}': {str(e)}",
                'data': None
            }
    
    def _search_by_email(self, email: str) -> Dict[str, Any]:
        """Search for people by email"""
        if not email.strip():
            return {
                'success': False,
                'message': "Please specify an email to search for.",
                'data': None
            }
        
        try:
            results = self.adls_handler.search_by_email(email.strip())
            
            if results:
                return {
                    'success': True,
                    'message': f"I found {len(results)} person(s) with email containing '{email}':",
                    'data': {
                        'results': results,
                        'query_type': 'search_by_email',
                        'search_term': email
                    }
                }
            else:
                return {
                    'success': True,
                    'message': f"No person found with email containing '{email}'.",
                    'data': {
                        'results': [],
                        'query_type': 'search_by_email',
                        'search_term': email
                    }
                }
        except Exception as e:
            return {
                'success': False,
                'message': f"Sorry, I couldn't search for email '{email}': {str(e)}",
                'data': None
            }
    
    def _get_recent_files(self, query: str) -> Dict[str, Any]:
        """Get recent files based on time period"""
        try:
            records = self.adls_handler.get_all_records(limit=100)
            
            # Determine time filter
            days_back = 7  # Default to last week
            if 'today' in query:
                days_back = 1
            elif 'yesterday' in query:
                days_back = 2
            elif 'this week' in query:
                days_back = 7
            elif 'last week' in query:
                days_back = 14
            
            # Filter by date
            cutoff_date = datetime.now() - timedelta(days=days_back)
            recent_records = []
            
            for record in records:
                created_date_str = record.get('created_date', '')
                try:
                    created_date = datetime.fromisoformat(created_date_str.replace('Z', '+00:00'))
                    if created_date >= cutoff_date:
                        recent_records.append(record)
                except:
                    continue
            
            period_name = "today" if days_back == 1 else f"last {days_back} days"
            
            return {
                'success': True,
                'message': f"I found {len(recent_records)} files processed in the {period_name}:",
                'data': {
                    'results': recent_records,
                    'query_type': 'recent_files',
                    'period': period_name
                }
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Sorry, I couldn't get recent files: {str(e)}",
                'data': None
            }
    
    def _get_files_by_type(self, doc_type: str) -> Dict[str, Any]:
        """Get files by document type"""
        try:
            records = self.adls_handler.get_all_records(limit=1000)
            
            if doc_type.strip():
                # Filter by document type
                filtered_records = [
                    record for record in records 
                    if record.get('document_type', '').lower().find(doc_type.lower()) != -1
                ]
                
                return {
                    'success': True,
                    'message': f"I found {len(filtered_records)} {doc_type} documents:",
                    'data': {
                        'results': filtered_records,
                        'query_type': 'files_by_type',
                        'document_type': doc_type
                    }
                }
            else:
                # Group by document type
                type_counts = {}
                for record in records:
                    doc_type = record.get('document_type', 'Unknown')
                    type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
                
                return {
                    'success': True,
                    'message': "Here's the breakdown by document type:",
                    'data': {
                        'type_counts': type_counts,
                        'query_type': 'files_by_type'
                    }
                }
        except Exception as e:
            return {
                'success': False,
                'message': f"Sorry, I couldn't get files by type: {str(e)}",
                'data': None
            }
    
    def _get_confidence_stats(self) -> Dict[str, Any]:
        """Get confidence score statistics"""
        try:
            records = self.adls_handler.get_all_records(limit=1000)
            
            confidence_scores = []
            for record in records:
                score = record.get('confidence_score')
                if score is not None and isinstance(score, (int, float)):
                    confidence_scores.append(float(score))
            
            if confidence_scores:
                avg_confidence = sum(confidence_scores) / len(confidence_scores)
                min_confidence = min(confidence_scores)
                max_confidence = max(confidence_scores)
                
                return {
                    'success': True,
                    'message': f"Confidence Statistics:",
                    'data': {
                        'average_confidence': round(avg_confidence, 2),
                        'min_confidence': round(min_confidence, 2),
                        'max_confidence': round(max_confidence, 2),
                        'total_records': len(confidence_scores),
                        'query_type': 'confidence_stats'
                    }
                }
            else:
                return {
                    'success': True,
                    'message': "No confidence score data available.",
                    'data': {'query_type': 'confidence_stats'}
                }
        except Exception as e:
            return {
                'success': False,
                'message': f"Sorry, I couldn't get confidence statistics: {str(e)}",
                'data': None
            }
    
    def _get_summary_stats(self) -> Dict[str, Any]:
        """Get overall summary statistics"""
        try:
            records = self.adls_handler.get_all_records(limit=1000)
            pdf_files = self.adls_handler.list_pdf_files()
            
            # Count unique people
            unique_emails = set()
            doc_types = {}
            confidence_scores = []
            
            for record in records:
                email = record.get('email', '').lower().strip()
                if email:
                    unique_emails.add(email)
                
                doc_type = record.get('document_type', 'Unknown')
                doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
                
                score = record.get('confidence_score')
                if score is not None and isinstance(score, (int, float)):
                    confidence_scores.append(float(score))
            
            avg_confidence = (sum(confidence_scores) / len(confidence_scores)) if confidence_scores else 0
            
            return {
                'success': True,
                'message': "Here's a summary of your document processing system:",
                'data': {
                    'total_pdf_files': len(pdf_files),
                    'total_processed_files': len(records),
                    'unique_people': len(unique_emails),
                    'document_types': doc_types,
                    'average_confidence': round(avg_confidence, 2),
                    'query_type': 'summary_stats'
                }
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Sorry, I couldn't generate summary statistics: {str(e)}",
                'data': None
            }
    
    def _handle_unknown_query(self, query: str) -> Dict[str, Any]:
        """Handle queries that don't match any pattern"""
        
        # If AI is available, try to provide a more helpful response
        if self.use_ai:
            try:
                response = self.openai_client.chat.completions.create(
                    model=self.config.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant for a PDF document processing system. The user asked a question that doesn't match our available functions. Provide a helpful response and suggest what they can ask about instead. Keep it brief and friendly."},
                        {"role": "user", "content": f"User asked: '{query}'. What would be a helpful response?"}
                    ],
                    temperature=0.7,
                    max_tokens=200
                )
                
                ai_response = response.choices[0].message.content
                
                return {
                    'success': False,
                    'message': ai_response,
                    'data': {
                        'suggestions': self._get_suggestions(),
                        'query_type': 'unknown',
                        'ai_enhanced': True
                    }
                }
            except:
                pass
        
        # Fallback to standard response
        suggestions = [
            "• How many files are processed?",
            "• How many people are in the system?",
            "• Find John Smith",
            "• Search for email john@example.com",
            "• Show me recent files",
            "• Give me summary statistics",
            "• Show confidence scores"
        ]
        
        return {
            'success': False,
            'message': f"I'm sorry, I didn't understand '{query}'. Here are some things you can ask me:",
            'data': {
                'suggestions': suggestions,
                'query_type': 'unknown'
            }
        }
    
    def _get_suggestions(self) -> List[str]:
        """Get helpful suggestions for user queries"""
        return [
            "How many files are processed?",
            "How many people are in the system?",
            "Find John Smith",
            "Search for email john@example.com",
            "Show me recent files",
            "Give me summary statistics",
            "Show confidence scores"
        ]
    
    def get_help(self) -> Dict[str, Any]:
        """Return help information about available queries"""
        examples = {
            "File Counts": [
                "How many files are processed?",
                "Total number of documents",
                "Count of PDFs"
            ],
            "People Counts": [
                "How many people are there?",
                "Number of employees",
                "Count of individuals"
            ],
            "Search by Name": [
                "Find John Smith",
                "Who is Mary Johnson?",
                "Search for Alex person"
            ],
            "Search by Email": [
                "Find email john@example.com",
                "Who has email mary@company.com"
            ],
            "Recent Files": [
                "Show me recent files",
                "Files processed today",
                "Documents from this week"
            ],
            "Statistics": [
                "Give me summary statistics",
                "Show confidence scores",
                "Extraction quality stats"
            ]
        }
        
        return {
            'success': True,
            'message': "Here are the types of questions you can ask me:" + (
                " (Enhanced with AI)" if self.use_ai else " (Pattern matching mode)"
            ),
            'data': {
                'examples': examples,
                'query_type': 'help',
                'ai_enabled': self.use_ai
            }
        }