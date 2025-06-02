import streamlit as st
import pandas as pd
from adls_handler import ADLSHandler
from document_intelligence import DocumentIntelligenceHandler
from query_engine import QueryEngine
import logging
import uuid
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)

class PDFChatbot:
    def __init__(self):
        self.adls_handler = ADLSHandler()
        self.doc_intelligence = DocumentIntelligenceHandler()
        self.query_engine = QueryEngine(self.adls_handler)
    
    def process_pdf_file(self, file_name):
        """Process a single PDF file"""
        try:
            # Download PDF from ADLS
            st.info(f"Downloading {file_name}...")
            pdf_content = self.adls_handler.download_pdf(file_name)
            
            if not pdf_content:
                st.error(f"Failed to download {file_name}")
                return None
            
            # Extract personal information
            st.info("Extracting personal information...")
            personal_info = self.doc_intelligence.extract_personal_info(pdf_content)
            
            if not personal_info:
                st.error("Failed to extract personal information")
                return None
            
            # Generate unique e-file ID
            e_file_id = str(uuid.uuid4())
            
            # Store in ADLS
            st.info("Storing in ADLS...")
            success = self.adls_handler.save_extracted_data(file_name, e_file_id, personal_info)
            
            if success:
                st.success(f"Successfully processed {file_name}")
                st.info(f"E-File ID: {e_file_id}")
                return e_file_id
            else:
                st.error("Failed to store in ADLS")
                return None
                
        except Exception as e:
            st.error(f"Error processing {file_name}: {str(e)}")
            return None
    
    def search_records(self, search_type, query):
        """Search records based on type and query"""
        try:
            if search_type == "E-File ID":
                result = self.adls_handler.get_extracted_data(query)
                if result:
                    # Convert to the format expected by the UI
                    return [{
                        'e_file_id': result['e_file_id'],
                        'file_name': result['source_file'],
                        'first_name': result['extracted_info'].get('first_name'),
                        'last_name': result['extracted_info'].get('last_name'),
                        'email': result['extracted_info'].get('email'),
                        'phone_number': result['extracted_info'].get('phone_number'),
                        'address': result['extracted_info'].get('address'),
                        'date_of_birth': result['extracted_info'].get('date_of_birth'),
                        'age': result['extracted_info'].get('age'),
                        'document_type': result['extracted_info'].get('document_type'),
                        'confidence_score': result['extracted_info'].get('confidence_score'),
                        'extracted_text': result['extracted_info'].get('extracted_text'),
                        'created_date': result.get('extraction_timestamp')
                    }]
                return []
            elif search_type == "Email":
                return self.adls_handler.search_by_email(query)
            elif search_type == "Name":
                return self.adls_handler.search_by_name(query)
            else:
                return []
        except Exception as e:
            st.error(f"Error searching records: {str(e)}")
            return []

def main():
    st.set_page_config(
        page_title="PDF Personal Information Extractor",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("📄 PDF Personal Information Extractor Chatbot")
    st.markdown("---")
    
    # Initialize chatbot with error handling
    if 'chatbot' not in st.session_state:
        try:
            with st.spinner("Initializing chatbot..."):
                st.session_state.chatbot = PDFChatbot()
            st.success("✅ Chatbot initialized successfully!")
        except Exception as e:
            st.error(f"❌ Failed to initialize chatbot: {str(e)}")
            st.error("Please check your configuration and try again.")
            
            # Show setup instructions
            with st.expander("🔧 Setup Instructions"):
                st.markdown("""
                **Common issues and solutions:**
                
                1. **Missing .env file**: Create a `.env` file in your project directory
                2. **Empty connection string**: Check your Azure Storage connection string
                3. **Missing credentials**: Ensure all Azure credentials are properly set
                
                **Steps to fix:**
                1. Run `python setup_checker.py` to diagnose issues
                2. Update your `.env` file with correct Azure credentials
                3. Restart the Streamlit app
                """)
            st.stop()
    
    chatbot = st.session_state.chatbot
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["💬 Chat with Bot", "Process PDFs", "Search Records", "View All Records", "Upload New PDF"]
    )
    
    if page == "💬 Chat with Bot":
        st.header("🤖 Chat with AI Assistant")
        
        # Show AI status
        ai_status = "🧠 AI-Enhanced" if chatbot.query_engine.use_ai else "🔧 Pattern Matching"
        st.markdown(f"**Status:** {ai_status}")
        st.markdown("Ask me questions about your processed documents and data!")
        
        # Custom CSS to make text input white
        st.markdown("""
        <style>
        /* Make text input boxes white with black text */
        .stTextInput > div > div > input {
            background-color: white !important;
            color: black !important;
            border: 2px solid #0066cc !important;
            border-radius: 5px !important;
        }
        
        /* Make text input label more visible */
        .stTextInput > label {
            color: white !important;
            font-weight: bold !important;
            font-size: 18px !important;
        }
        
        /* Style the main input section */
        .main-input-section {
            background-color: #1e1e1e;
            padding: 20px;
            border-radius: 10px;
            border: 3px solid #0066cc;
            margin: 20px 0;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Initialize chat history
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        # PROMINENT INPUT SECTION - Put this at the top!
        st.markdown('<div class="main-input-section">', unsafe_allow_html=True)
        st.markdown("# 💬 TYPE YOUR QUESTION HERE:")
        
        # Simple, direct input with white background
        user_question = st.text_input(
            "Ask me anything about your documents:",
            placeholder="Example: How many files are processed?",
            key="user_input_main",
            help="This text box should now be white!"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Big, obvious send button
        if st.button("🚀 ASK QUESTION", type="primary", use_container_width=True):
            if user_question.strip():
                with st.spinner("🤔 Processing your question..."):
                    response = chatbot.query_engine.process_query(user_question.strip())
                
                st.session_state.chat_history.append((user_question.strip(), response))
                
                # Show the response immediately
                st.success("✅ Question processed!")
                
                # Show AI-enhanced response if available
                if response.get('ai_enhanced') and response.get('ai_response'):
                    st.markdown(f"**🧠 AI Response:** {response['ai_response']}")
                
                st.markdown(f"**🤖 Answer:** {response['message']}")
                
                # Display data if available
                if response.get('success') and response.get('data'):
                    data = response['data']
                    
                    if data.get('query_type') == 'summary_stats':
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("PDF Files", data.get('total_pdf_files', 0))
                        with col2:
                            st.metric("Processed Files", data.get('total_processed_files', 0))
                        with col3:
                            st.metric("Unique People", data.get('unique_people', 0))
                        with col4:
                            st.metric("Avg Confidence", f"{data.get('average_confidence', 0):.2f}")
                    
                    elif data.get('results') and isinstance(data['results'], list):
                        if len(data['results']) > 0:
                            df = pd.DataFrame(data['results'])
                            st.dataframe(df, use_container_width=True)
        
        # Quick buttons - Make them very prominent
        st.markdown("---")
        st.markdown("# 🚀 OR CLICK THESE QUICK OPTIONS:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 SHOW SUMMARY STATS", use_container_width=True, type="secondary"):
                response = chatbot.query_engine.process_query("give me summary statistics")
                st.session_state.chat_history.append(("Show Summary", response))
                st.success("✅ Summary Stats:")
                st.markdown(f"**🤖 Answer:** {response['message']}")
                
                if response.get('data'):
                    data = response['data']
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("PDF Files", data.get('total_pdf_files', 0))
                    with col2:
                        st.metric("Processed Files", data.get('total_processed_files', 0))
                    with col3:
                        st.metric("Unique People", data.get('unique_people', 0))
                    with col4:
                        st.metric("Avg Confidence", f"{data.get('average_confidence', 0):.2f}")
        
        with col2:
            if st.button("📁 COUNT ALL FILES", use_container_width=True, type="secondary"):
                response = chatbot.query_engine.process_query("how many files are processed")
                st.session_state.chat_history.append(("Count Files", response))
                st.success("✅ File Count:")
                st.markdown(f"**🤖 Answer:** {response['message']}")
        
        col3, col4 = st.columns(2)
        
        with col3:
            if st.button("👥 COUNT ALL PEOPLE", use_container_width=True, type="secondary"):
                response = chatbot.query_engine.process_query("how many people are there")
                st.session_state.chat_history.append(("Count People", response))
                st.success("✅ People Count:")
                st.markdown(f"**🤖 Answer:** {response['message']}")
        
        with col4:
            if st.button("📋 DOCUMENT TYPES", use_container_width=True, type="secondary"):
                response = chatbot.query_engine.process_query("what kind of documents do I have")
                st.session_state.chat_history.append(("Document Types", response))
                st.success("✅ Document Types:")
                st.markdown(f"**🤖 Answer:** {response['message']}")
                
                if response.get('data') and response['data'].get('type_counts'):
                    st.bar_chart(response['data']['type_counts'])
        
        # Additional row of buttons
        col5, col6 = st.columns(2)
        
        with col5:
            if st.button("🕒 SHOW RECENT FILES", use_container_width=True, type="secondary"):
                response = chatbot.query_engine.process_query("show me recent files")
                st.session_state.chat_history.append(("Recent Files", response))
                st.success("✅ Recent Files:")
                st.markdown(f"**🤖 Answer:** {response['message']}")
                
                if response.get('data') and response['data'].get('results'):
                    df = pd.DataFrame(response['data']['results'])
                    # Show key columns including date_of_birth
                    display_columns = ['file_name', 'first_name', 'last_name', 'email', 'date_of_birth', 'age', 'created_date']
                    available_columns = [col for col in display_columns if col in df.columns]
                    st.dataframe(df[available_columns], use_container_width=True)
        
        with col6:
            if st.button("📈 CONFIDENCE STATS", use_container_width=True, type="secondary"):
                response = chatbot.query_engine.process_query("show confidence scores")
                st.session_state.chat_history.append(("Confidence Stats", response))
                st.success("✅ Confidence Stats:")
                st.markdown(f"**🤖 Answer:** {response['message']}")
                
                if response.get('data'):
                    data = response['data']
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Average", f"{data.get('average_confidence', 0):.2f}")
                    with col2:
                        st.metric("Min", f"{data.get('min_confidence', 0):.2f}")
                    with col3:
                        st.metric("Max", f"{data.get('max_confidence', 0):.2f}")
                    with col4:
                        st.metric("Records", data.get('total_records', 0))
        
        # Show chat history at the bottom
        if st.session_state.chat_history:
            st.markdown("---")
            st.markdown("# 📜 CONVERSATION HISTORY:")
            
            for i, (user_msg, bot_response) in enumerate(st.session_state.chat_history):
                st.markdown(f"**🧑 Question {i+1}:** {user_msg}")
                st.markdown(f"**🤖 Answer {i+1}:** {bot_response['message']}")
                st.markdown("---")
        
        # Clear button
        if st.button("🗑️ CLEAR HISTORY", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()
    
    elif page == "Process PDFs":
        st.header("🔄 Process PDF Files from ADLS Storage")
        
        # List available PDF files
        if st.button("Refresh PDF List"):
            st.session_state.pdf_files = chatbot.adls_handler.list_pdf_files()
        
        if 'pdf_files' not in st.session_state:
            st.session_state.pdf_files = chatbot.adls_handler.list_pdf_files()
        
        if st.session_state.pdf_files:
            st.subheader("Available PDF Files:")
            
            # Display files in a table
            df = pd.DataFrame(st.session_state.pdf_files)
            df['last_modified'] = pd.to_datetime(df['last_modified']).dt.strftime('%Y-%m-%d %H:%M:%S')
            df['size'] = df['size'].apply(lambda x: f"{x/1024:.1f} KB")
            
            st.dataframe(df[['name', 'size', 'last_modified']], use_container_width=True)
            
            # Process individual files
            st.subheader("Process Files:")
            selected_file = st.selectbox(
                "Select a file to process:",
                options=[f['name'] for f in st.session_state.pdf_files]
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Process Selected File"):
                    e_file_id = chatbot.process_pdf_file(selected_file)
                    if e_file_id:
                        st.session_state.last_processed_id = e_file_id
            
            with col2:
                if st.button("Process All Files"):
                    progress_bar = st.progress(0)
                    total_files = len(st.session_state.pdf_files)
                    
                    for i, file_info in enumerate(st.session_state.pdf_files):
                        st.write(f"Processing {file_info['name']}...")
                        chatbot.process_pdf_file(file_info['name'])
                        progress_bar.progress((i + 1) / total_files)
                    
                    st.success("All files processed!")
        else:
            st.info("No PDF files found in ADLS storage.")
    
    elif page == "Search Records":
        st.header("🔍 Search Personal Information Records")
        
        col1, col2 = st.columns(2)
        
        with col2:
            search_type = st.selectbox(
                "Search by:",
                ["E-File ID", "Email", "Name"]
            )
        
        with col1:
            query = st.text_input(f"Enter {search_type}:")
        
        if st.button("Search") and query:
            results = chatbot.search_records(search_type, query)
            
            if results:
                st.success(f"Found {len(results)} record(s)")
                
                for result in results:
                    with st.expander(f"Record: {result.get('e_file_id', 'Unknown')}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**E-File ID:** {result.get('e_file_id', 'N/A')}")
                            st.write(f"**File Name:** {result.get('file_name', 'N/A')}")
                            st.write(f"**First Name:** {result.get('first_name', 'N/A')}")
                            st.write(f"**Last Name:** {result.get('last_name', 'N/A')}")
                            st.write(f"**Email:** {result.get('email', 'N/A')}")
                        
                        with col2:
                            st.write(f"**Phone:** {result.get('phone_number', 'N/A')}")
                            st.write(f"**Address:** {result.get('address', 'N/A')}")
                            st.write(f"**DOB:** {result.get('date_of_birth', 'N/A')}")
                            st.write(f"**Age:** {result.get('age', 'N/A')}")
                            st.write(f"**Document Type:** {result.get('document_type', 'N/A')}")
                            st.write(f"**Confidence:** {result.get('confidence_score', 'N/A')}")
                        
                        if 'extracted_text' in result and result['extracted_text']:
                            st.text_area("Extracted Text:", result['extracted_text'], height=100)
            else:
                st.info("No records found.")
    
    elif page == "View All Records":
        st.header("📋 All Personal Information Records")
        
        # Get all records
        records = chatbot.adls_handler.get_all_records(limit=100)
        
        if records:
            st.info(f"Showing {len(records)} most recent records")
            
            # Convert to DataFrame for better display
            df = pd.DataFrame(records)
            
            # Format datetime columns
            if 'created_date' in df.columns:
                df['created_date'] = pd.to_datetime(df['created_date']).dt.strftime('%Y-%m-%d %H:%M')
            
            # Display in a table
            st.dataframe(df, use_container_width=True)
            
            # Download as CSV
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download as CSV",
                data=csv,
                file_name=f"personal_info_records_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No records found in ADLS storage.")
    
    elif page == "Upload New PDF":
        st.header("📤 Upload New PDF File")
        
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type="pdf",
            help="Upload a PDF file to process and extract personal information"
        )
        
        if uploaded_file is not None:
            # Display file details
            st.write(f"**File name:** {uploaded_file.name}")
            st.write(f"**File size:** {uploaded_file.size / 1024:.1f} KB")
            
            if st.button("Upload and Process"):
                try:
                    # Upload to ADLS
                    st.info("Uploading to ADLS...")
                    file_content = uploaded_file.read()
                    
                    success = chatbot.adls_handler.upload_pdf(uploaded_file.name, file_content)
                    
                    if success:
                        st.success("File uploaded successfully!")
                        
                        # Process the uploaded file
                        st.info("Processing uploaded file...")
                        e_file_id = chatbot.process_pdf_file(uploaded_file.name)
                        
                        if e_file_id:
                            st.success(f"File processed successfully! E-File ID: {e_file_id}")
                        else:
                            st.error("Failed to process uploaded file")
                    else:
                        st.error("Failed to upload file to ADLS")
                        
                except Exception as e:
                    st.error(f"Error uploading file: {str(e)}")
    
    # Footer
    st.markdown("---")
    
    # Quick stats in sidebar
    with st.sidebar:
        st.markdown("---")
        st.subheader("📊 Quick Stats")
        try:
            # Get quick stats
            all_records = chatbot.adls_handler.get_all_records(limit=1000)
            pdf_files = chatbot.adls_handler.list_pdf_files()
            
            st.metric("PDF Files", len(pdf_files))
            st.metric("Processed Files", len(all_records))
            
            # Count unique people
            unique_emails = set()
            for record in all_records:
                email = record.get('email', '').strip()
                if email:
                    unique_emails.add(email.lower())
            
            st.metric("Unique People", len(unique_emails))
            
        except Exception as e:
            st.error(f"Could not load stats: {str(e)}")
    
    st.markdown("💡 **Tips:** Use the chat interface to ask questions about your data, or navigate to specific functions using the sidebar.")

if __name__ == "__main__":
    main()