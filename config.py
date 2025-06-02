import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    def __init__(self):
        # Azure Data Lake Storage Gen2
        self.ADLS_ACCOUNT_NAME = os.getenv('ADLS_ACCOUNT_NAME')
        self.ADLS_ACCOUNT_KEY = os.getenv('ADLS_ACCOUNT_KEY')
        self.ADLS_FILESYSTEM_NAME = os.getenv('ADLS_FILESYSTEM_NAME', 'chatbot-data')
        
        # Azure Document Intelligence
        self.DOCUMENT_INTELLIGENCE_ENDPOINT = os.getenv('DOCUMENT_INTELLIGENCE_ENDPOINT')
        self.DOCUMENT_INTELLIGENCE_KEY = os.getenv('DOCUMENT_INTELLIGENCE_KEY')
        
        # OpenAI Configuration
        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        self.OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        
        # Azure OpenAI (alternative)
        self.AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
        self.AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
        self.AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
        
        # ADLS Directory Structure
        self.PDF_DIRECTORY = "pdfs"
        self.EXTRACTED_DATA_DIRECTORY = "extracted-data"
        self.METADATA_DIRECTORY = "metadata"
        
        # Validate required environment variables
        self._validate_config()
    
    def _validate_config(self):
        """Validate that all required environment variables are set"""
        required_vars = {
            'ADLS_ACCOUNT_NAME': self.ADLS_ACCOUNT_NAME,
            'ADLS_ACCOUNT_KEY': self.ADLS_ACCOUNT_KEY,
            'DOCUMENT_INTELLIGENCE_ENDPOINT': self.DOCUMENT_INTELLIGENCE_ENDPOINT,
            'DOCUMENT_INTELLIGENCE_KEY': self.DOCUMENT_INTELLIGENCE_KEY
        }
        
        # Check if either OpenAI or Azure OpenAI is configured
        has_openai = bool(self.OPENAI_API_KEY)
        has_azure_openai = bool(self.AZURE_OPENAI_ENDPOINT and self.AZURE_OPENAI_API_KEY)
        
        if not (has_openai or has_azure_openai):
            print("⚠️  Warning: No OpenAI configuration found. AI features will use basic pattern matching.")
        
        missing_vars = [var_name for var_name, var_value in required_vars.items() if not var_value]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}. Please check your .env file.")
    
    @property
    def adls_account_url(self):
        return f"https://{self.ADLS_ACCOUNT_NAME}.dfs.core.windows.net"
    
    @property
    def use_openai(self):
        """Check if OpenAI is configured and should be used"""
        return bool(self.OPENAI_API_KEY)
    
    @property
    def use_azure_openai(self):
        """Check if Azure OpenAI is configured and should be used"""
        return bool(self.AZURE_OPENAI_ENDPOINT and self.AZURE_OPENAI_API_KEY)