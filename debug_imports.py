#!/usr/bin/env python3
"""
Debug script to check import issues
"""

print("Testing imports step by step...")

try:
    print("1. Testing azure.storage.filedatalake...")
    from azure.storage.filedatalake import DataLakeServiceClient
    print("✅ azure.storage.filedatalake imported successfully")
except ImportError as e:
    print(f"❌ Failed to import azure.storage.filedatalake: {e}")

try:
    print("2. Testing azure.core.credentials...")
    from azure.core.credentials import AzureNamedKeyCredential
    print("✅ azure.core.credentials imported successfully")
except ImportError as e:
    print(f"❌ Failed to import azure.core.credentials: {e}")

try:
    print("3. Testing config...")
    from config import Config
    print("✅ config imported successfully")
except ImportError as e:
    print(f"❌ Failed to import config: {e}")
    print("This might be due to missing .env file or environment variables")

try:
    print("4. Testing other standard libraries...")
    import logging
    import json
    import uuid
    from datetime import datetime
    import io
    print("✅ Standard libraries imported successfully")
except ImportError as e:
    print(f"❌ Failed to import standard libraries: {e}")

try:
    print("5. Testing adls_handler...")
    import adls_handler
    print("✅ adls_handler module imported successfully")
    
    print("6. Testing ADLSHandler class...")
    from adls_handler import ADLSHandler
    print("✅ ADLSHandler class imported successfully")
    
except ImportError as e:
    print(f"❌ Failed to import from adls_handler: {e}")
except Exception as e:
    print(f"❌ Error during import: {e}")

print("\nDone!")