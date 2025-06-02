import argparse
from adls_handler import ADLSHandler
from document_intelligence import DocumentIntelligenceHandler
import json
import uuid

class CLIChatbot:
    def __init__(self):
        self.adls_handler = ADLSHandler()
        self.doc_intelligence = DocumentIntelligenceHandler()
    
    def list_files(self):
        """List all PDF files in ADLS storage"""
        files = self.adls_handler.list_pdf_files()
        print(f"\nFound {len(files)} PDF files:")
        for i, file in enumerate(files, 1):
            print(f"{i}. {file['name']} - {file['size']/1024:.1f} KB")
        return files
    
    def process_file(self, filename):
        """Process a specific file"""
        print(f"\nProcessing {filename}...")
        
        # Download PDF
        pdf_content = self.adls_handler.download_pdf(filename)
        if not pdf_content:
            print("Failed to download file")
            return
        
        # Extract information
        personal_info = self.doc_intelligence.extract_personal_info(pdf_content)
        if not personal_info:
            print("Failed to extract information")
            return
        
        # Generate e-file ID and store in ADLS
        e_file_id = str(uuid.uuid4())
        success = self.adls_handler.save_extracted_data(filename, e_file_id, personal_info)
        
        if success:
            print(f"Successfully processed! E-File ID: {e_file_id}")
            print("\nExtracted Information:")
            for key, value in personal_info.items():
                if key != 'extracted_text' and value:
                    print(f"  {key}: {value}")
        else:
            print("Failed to store in ADLS")
    
    def search_by_email(self, email):
        """Search records by email"""
        results = self.adls_handler.search_by_email(email)
        if results:
            print(f"\nFound {len(results)} record(s):")
            for result in results:
                print(f"\nE-File ID: {result['e_file_id']}")
                print(f"Name: {result.get('first_name', '')} {result.get('last_name', '')}")
                print(f"Email: {result.get('email', '')}")
                print(f"Phone: {result.get('phone_number', '')}")
        else:
            print("No records found")
    
    def search_by_name(self, name):
        """Search records by name"""
        results = self.adls_handler.search_by_name(name)
        if results:
            print(f"\nFound {len(results)} record(s):")
            for result in results:
                print(f"\nE-File ID: {result['e_file_id']}")
                print(f"Name: {result.get('first_name', '')} {result.get('last_name', '')}")
                print(f"Email: {result.get('email', '')}")
                print(f"Phone: {result.get('phone_number', '')}")
        else:
            print("No records found")
    
    def get_record(self, e_file_id):
        """Get record by E-File ID"""
        result = self.adls_handler.get_extracted_data(e_file_id)
        if result:
            print(f"\nRecord found:")
            print(f"  E-File ID: {result['e_file_id']}")
            print(f"  Source File: {result['source_file']}")
            print(f"  Extraction Date: {result['extraction_timestamp']}")
            print("\nExtracted Information:")
            for key, value in result['extracted_info'].items():
                if key != 'extracted_text' and value:
                    print(f"  {key}: {value}")
        else:
            print("Record not found")

def main():
    parser = argparse.ArgumentParser(description="PDF Personal Information Extractor CLI")
    parser.add_argument('--chat', action='store_true', help='Start interactive chat mode')
    parser.add_argument('--list', action='store_true', help='List all PDF files')
    parser.add_argument('--process', type=str, help='Process a specific PDF file')
    parser.add_argument('--search-email', type=str, help='Search by email')
    parser.add_argument('--search-name', type=str, help='Search by name')
    parser.add_argument('--get-record', type=str, help='Get record by E-File ID')
    parser.add_argument('--process-all', action='store_true', help='Process all PDF files')
    parser.add_argument('--query', type=str, help='Ask a natural language question')
    
    args = parser.parse_args()
    
    chatbot = CLIChatbot()
    
    if args.chat:
        chatbot.interactive_chat()
    elif args.query:
        chatbot.quick_query(args.query)
    elif args.list:
        chatbot.list_files()
    elif args.process:
        chatbot.process_file(args.process)
    elif args.search_email:
        chatbot.search_by_email(args.search_email)
    elif args.search_name:
        chatbot.search_by_name(args.search_name)
    elif args.get_record:
        chatbot.get_record(args.get_record)
    elif args.process_all:
        files = chatbot.list_files()
        for file in files:
            chatbot.process_file(file['name'])
    else:
        parser.print_help()
        print("\n💡 Try: --chat for interactive mode, or --query 'How many files?'")

if __name__ == "__main__":
    main()