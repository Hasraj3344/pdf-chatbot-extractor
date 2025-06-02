# 📄 PDF Personal Information Extractor Chatbot

An intelligent chatbot system that processes PDF documents, extracts personal information using Azure AI services, and provides conversational query capabilities powered by OpenAI.

## 🚀 Features

- **PDF Processing**: Upload and process PDF documents from Azure Data Lake Storage
- **AI-Powered Extraction**: Uses Azure Document Intelligence to extract personal information
- **Age to DOB Conversion**: Automatically converts age to date of birth
- **Conversational AI**: OpenAI-powered natural language query interface
- **Data Storage**: Stores extracted data in Azure Data Lake Storage as JSON
- **Search & Filter**: Search by name, email, document type, and more
- **Interactive Dashboard**: Streamlit-based web interface with real-time statistics

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **AI/ML**: Azure Document Intelligence, OpenAI GPT
- **Storage**: Azure Data Lake Storage Gen2
- **Backend**: Python
- **Data Processing**: Pandas, JSON

## 📋 Prerequisites

- Python 3.8+
- Azure Account with:
  - Azure Data Lake Storage Gen2
  - Azure Document Intelligence (Form Recognizer)
- OpenAI API Key

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/pdf-chatbot-extractor.git
   cd pdf-chatbot-extractor
   ```

2. **Create virtual environment**
   ```bash
   python -m venv chatbot_env
   # On Windows:
   chatbot_env\Scripts\activate
   # On macOS/Linux:
   source chatbot_env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your actual credentials
   ```

5. **Run setup checker**
   ```bash
   python setup_checker.py
   ```

## ⚙️ Configuration

Create a `.env` file with your Azure and OpenAI credentials:

```bash
# Azure Data Lake Storage Gen2
ADLS_ACCOUNT_NAME="your_storage_account"
ADLS_ACCOUNT_KEY="your_storage_key"
ADLS_FILESYSTEM_NAME="chatbot-data"

# Azure Document Intelligence
DOCUMENT_INTELLIGENCE_ENDPOINT="https://your-resource.cognitiveservices.azure.com/"
DOCUMENT_INTELLIGENCE_KEY="your_document_intelligence_key"

# OpenAI API
OPENAI_API_KEY="sk-your_openai_api_key"
OPENAI_MODEL="gpt-3.5-turbo"
```

## 🚀 Usage

### Web Interface
```bash
streamlit run chatbot.py
```

### Command Line Interface
```bash
# Interactive chat mode
python cli_chatbot.py --chat

# Quick queries
python cli_chatbot.py --query "How many files are processed?"

# List files
python cli_chatbot.py --list

# Process specific file
python cli_chatbot.py --process "document.pdf"
```

## 💬 Example Queries

The chatbot understands natural language queries:

- "How many files are processed?"
- "How many people are in the system?"
- "Find John Smith"
- "What kind of documents do I have?"
- "Show me recent files"
- "Give me summary statistics"
- "Search for email john@example.com"

## 📁 Project Structure

```
pdf-chatbot-extractor/
├── chatbot.py                 # Main Streamlit web application
├── cli_chatbot.py            # Command-line interface
├── adls_handler_simple.py    # Azure Data Lake Storage operations
├── document_intelligence.py  # AI document processing
├── query_engine.py          # Natural language query processing
├── config.py                # Configuration management
├── setup_checker.py         # Setup validation script
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variables template
├── .env                     # Your actual environment variables (not in repo)
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## 🔍 Key Components

### Document Processing
- Extracts personal information (name, email, phone, address, age)
- Converts age to date of birth automatically
- Supports multiple document types (passport, ID, resume, etc.)
- Confidence scoring for extraction quality

### Data Storage
- Hierarchical structure in Azure Data Lake Storage:
  - `pdfs/` - Original PDF files
  - `extracted-data/` - JSON files with extracted information
  - `metadata/` - Search indexes and metadata

### AI Features
- OpenAI-powered query understanding
- Pattern matching fallback for reliability
- Context-aware responses
- Natural language processing

## 📊 ADLS Directory Structure

```
chatbot-data/
├── pdfs/                    # Original PDF files
│   ├── document1.pdf
│   └── document2.pdf
├── extracted-data/          # JSON files with extracted information
│   ├── uuid1.json
│   └── uuid2.json
└── metadata/               # Search indexes and metadata
    └── search_index.json
```

## 🛡️ Security

- Environment variables for sensitive credentials
- No hardcoded API keys in source code
- Secure Azure authentication
- Data encrypted in transit and at rest

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Azure Document Intelligence for AI-powered extraction
- OpenAI for natural language processing
- Streamlit for the interactive web interface

## 📞 Support

If you encounter any issues or have questions:
1. Check the [Issues](https://github.com/yourusername/pdf-chatbot-extractor/issues) page
2. Run `python setup_checker.py` to diagnose configuration problems
3. Create a new issue with detailed description

## 🔄 Version History

- **v1.0.0** - Initial release with basic PDF processing
- **v1.1.0** - Added OpenAI integration and conversational AI
- **v1.2.0** - Enhanced age to DOB conversion and improved UI

---

⭐ **Star this repository if you find it helpful!** ⭐