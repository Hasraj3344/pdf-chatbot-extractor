from dotenv import load_dotenv
import os
from azure.storage.blob import BlobServiceClient

def test_azure_connection():
    # Load environment variables
    load_dotenv()
    
    # Get connection string
    connection_string = os.getenv("AZURE_BLOB_CONNECTION_STRING")
    if not connection_string:
        print("❌ Error: AZURE_BLOB_CONNECTION_STRING not found in .env file")
        return False
    
    try:
        # Try to create a client
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        # List containers to test connection
        containers = list(blob_service_client.list_containers(max_results=1))
        
        print("✅ Successfully connected to Azure Blob Storage!")
        print(f"Account: {blob_service_client.account_name}")
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to Azure Blob Storage: {str(e)}")
        return False

if __name__ == "__main__":
    test_azure_connection() 