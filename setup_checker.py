#!/usr/bin/env python3
"""
Setup checker script to validate environment configuration
"""
import os
import sys
from dotenv import load_dotenv

def check_env_file():
    """Check if .env file exists and is readable"""
    env_path = '.env'
    if not os.path.exists(env_path):
        print("❌ .env file not found in current directory")
        print("📝 Please create a .env file with your Azure credentials")
        return False
    
    if not os.access(env_path, os.R_OK):
        print("❌ .env file exists but is not readable")
        return False
    
    print("✅ .env file found and readable")
    return True

def check_environment_variables():
    """Check if all required environment variables are set"""
    load_dotenv()
    
    required_vars = [
        'ADLS_ACCOUNT_NAME',
        'ADLS_ACCOUNT_KEY',
        'DOCUMENT_INTELLIGENCE_ENDPOINT',
        'DOCUMENT_INTELLIGENCE_KEY'
    ]
    
    missing_vars = []
    empty_vars = []
    
    print("\n🔍 Checking environment variables:")
    for var in required_vars:
        value = os.getenv(var)
        if value is None:
            missing_vars.append(var)
            print(f"❌ {var}: Not set")
        elif value.strip() == "":
            empty_vars.append(var)
            print(f"⚠️  {var}: Empty")
        else:
            # Show partial value for security
            if 'KEY' in var or 'PASSWORD' in var or 'CONNECTION_STRING' in var:
                display_value = value[:10] + "..." if len(value) > 10 else "***"
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
    
    if missing_vars or empty_vars:
        print(f"\n❌ Issues found:")
        if missing_vars:
            print(f"Missing variables: {', '.join(missing_vars)}")
        if empty_vars:
            print(f"Empty variables: {', '.join(empty_vars)}")
        return False
    
    print("\n✅ All environment variables are set")
    return True

def test_azure_connections():
    """Test connections to Azure services"""
    print("\n🔌 Testing Azure connections:")
    
    try:
        from config import Config
        config = Config()
        print("✅ Configuration loaded successfully")
    except Exception as e:
        print(f"❌ Configuration failed: {str(e)}")
        return False
    
    # Test ADLS
    try:
        from adls_handler import ADLSHandler
        adls_handler = ADLSHandler()
        if adls_handler.test_connection():
            print("✅ ADLS connection successful")
        else:
            print("❌ ADLS connection failed")
    except Exception as e:
        print(f"❌ ADLS error: {str(e)}")
    
    # Test Document Intelligence
    try:
        from document_intelligence import DocumentIntelligenceHandler
        doc_handler = DocumentIntelligenceHandler()
        print("✅ Document Intelligence client initialized")
    except Exception as e:
        print(f"❌ Document Intelligence error: {str(e)}")
    
    # Test Database - Not needed for ADLS version
    print("✅ Database not required (using ADLS for storage)")

def check_dependencies():
    """Check if all required Python packages are installed"""
    print("\n📦 Checking Python dependencies:")
    
    # Map of package names to their import names
    required_packages = {
        'azure-storage-file-datalake': 'azure.storage.filedatalake',
        'azure-ai-formrecognizer': 'azure.ai.formrecognizer',
        'python-dotenv': 'dotenv',
        'streamlit': 'streamlit',
        'pandas': 'pandas'
    }
    
    missing_packages = []
    
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            missing_packages.append(package_name)
            print(f"❌ {package_name}")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install " + " ".join(missing_packages))
        return False
    
    print("\n✅ All dependencies are installed")
    return True

def main():
    print("🚀 PDF Chatbot Setup Checker")
    print("=" * 40)
    
    all_good = True
    
    # Check .env file
    if not check_env_file():
        all_good = False
    
    # Check dependencies
    if not check_dependencies():
        all_good = False
    
    # Check environment variables
    if not check_environment_variables():
        all_good = False
    
    # Test Azure connections (only if env vars are set)
    if all_good:
        test_azure_connections()
    
    print("\n" + "=" * 40)
    if all_good:
        print("🎉 Setup looks good! You can run the chatbot.")
        print("Run: streamlit run chatbot.py")
    else:
        print("❌ Setup incomplete. Please fix the issues above.")
        print("\n📖 Quick setup guide:")
        print("1. Create .env file with your Azure credentials")
        print("2. Install missing packages: pip install -r requirements.txt")
        print("3. Run this checker again: python setup_checker.py")

if __name__ == "__main__":
    main()