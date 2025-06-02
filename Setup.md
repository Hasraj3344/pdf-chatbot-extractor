# 🚀 Detailed Setup Instructions

## Prerequisites

### 1. Azure Services Setup

#### Azure Data Lake Storage Gen2
1. Create a new Storage Account in Azure Portal
2. Enable "Hierarchical namespace" (this makes it ADLS Gen2)
3. Go to "Access keys" and copy:
   - Storage account name
   - Key1 or Key2

#### Azure Document Intelligence
1. Create a "Document Intelligence" resource in Azure Portal
2. Go to "Keys and Endpoint" and copy:
   - Endpoint URL
   - Key1 or Key2

### 2. OpenAI Setup
1. Visit https://platform.openai.com/api-keys
2. Create a new API key
3. Copy the key (starts with `sk-...`)

### 3. System Requirements
- Python 3.8 or higher
- Git
- 4GB+ RAM recommended

## Installation Steps

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/pdf-chatbot-extractor.git
cd pdf-chatbot-extractor
```

### 2. Setup Python Environment
```bash
# Create virtual environment
python -m venv chatbot_env

# Activate virtual environment
# Windows:
chatbot_env\Scripts\activate
# macOS/Linux:
source chatbot_env/bin/activate

# Upgrade pip
python -m pip install --upgrade pip
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
# Copy template
cp .env.example .env

# Edit .env file with your credentials
nano .env  # or use your preferred editor
```

### 5. Validate Setup
```bash
python setup_checker.py
```

## Configuration Details

### Environment Variables Explained

| Variable | Description | Example |
|----------|-------------|---------|
| `ADLS_ACCOUNT_NAME` | Your Azure Storage account name | `mystorageaccount` |
| `ADLS_ACCOUNT_KEY` | Azure Storage access key | `abc123def456...` |
| `ADLS_FILESYSTEM_NAME` | Container name in ADLS | `chatbot-data` |
| `DOCUMENT_INTELLIGENCE_ENDPOINT` | Azure AI endpoint URL | `https://mydocai.cognitiveservices.azure.com/` |
| `DOCUMENT_INTELLIGENCE_KEY` | Azure AI access key | `xyz789abc123...` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-abc123def456...` |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-3.5-turbo` |

### Optional: Azure OpenAI Setup

If you prefer Azure OpenAI over OpenAI API:

1. Create an Azure OpenAI resource
2. Deploy a model (e.g., gpt-35-turbo)
3. Uncomment and fill these variables in `.env`:
   ```bash
   AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
   AZURE_OPENAI_API_KEY="your_azure_openai_key"
   AZURE_OPENAI_DEPLOYMENT_NAME="gpt-35-turbo"
   ```

## Testing Your Setup

### 1. Run Setup Checker
```bash
python setup_checker.py
```

You should see all green checkmarks:
```
✅ .env file found and readable
✅ All dependencies are installed
✅ All environment variables are set
✅ ADLS connection successful
✅ Document Intelligence client initialized
```

### 2. Start the Application
```bash
streamlit run chatbot.py
```

### 3. Test Basic Functionality
1. Go to "Upload New PDF" and upload a test document
2. Process the document
3. Try the chat interface with queries like "How many files?"

## Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# If you see "ImportError: cannot import name..."
pip install --force-reinstall -r requirements.txt
```

#### 2. Azure Connection Errors
- Verify your storage account name and key
- Check if ADLS Gen2 is enabled (hierarchical namespace)
- Ensure your Azure subscription is active

#### 3. OpenAI API Errors
- Verify your API key is correct
- Check your OpenAI account has sufficient credits
- Ensure you're using the correct model name

#### 4. Document Intelligence Errors
- Verify endpoint URL (should end with `/`)
- Check your Azure subscription limits
- Ensure the resource is in the correct region

### Debug Mode

Run with verbose logging:
```bash
export PYTHONPATH="${PYTHONPATH}:."
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from setup_checker import main
main()
"
```

## Development Setup

### Code Formatting
```bash
pip install black flake8
black .
flake8 .
```

### Running Tests
```bash
pip install pytest
pytest
```

### Pre-commit Hooks
```bash
pip install pre-commit
pre-commit install
```

## Performance Optimization

### For Large Document Processing
- Increase Azure AI service tier
- Use batch processing for multiple files
- Consider Azure Container Instances for scaling

### For High Query Volume
- Implement caching for frequently accessed data
- Use Azure Redis Cache
- Optimize search index structure

## Security Best Practices

1. **Never commit `.env` file to git**
2. **Rotate API keys regularly**
3. **Use Azure Key Vault for production**
4. **Enable Azure Storage firewall rules**
5. **Monitor API usage and costs**

## Getting Help

1. **Documentation**: Check this README and SETUP.md
2. **Issues**: Search existing GitHub issues
3. **Support**: Create a new issue with:
   - Your setup checker output
   - Error messages
   - Steps to reproduce
   - Environment details (OS, Python version)

## Next Steps

After successful setup:
1. Upload some test PDF documents
2. Explore the chat interface
3. Customize extraction patterns for your use case
4. Set up monitoring and alerts
5. Consider deploying to Azure App Service