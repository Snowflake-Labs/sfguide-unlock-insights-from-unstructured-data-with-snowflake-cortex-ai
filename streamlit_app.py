import streamlit as st
import pandas as pd
import json
import os
import io
import logging
from typing import Dict, List, Optional, Any, Union
import html
import re
from pathlib import Path

# Snowflake-specific imports
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark import DataFrame
from datetime import datetime
from streamlit_extras.stylable_container import stylable_container

# Configure logging with more specific format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure Streamlit page layout - MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(layout="wide", page_title="AI Tools App", page_icon="❄️")

class SecureSnowflakeApp:
    """Enhanced secure Snowflake application with improved error handling and validation"""

    # Class-level constants for better performance
    SUPPORTED_LANGUAGES = {
        "Arabic": "ar", "English": "en", "French": "fr", "German": "de",
        "Hindi": "hi", "Italian": "it", "Japanese": "ja", "Korean": "ko",
        "Polish": "pl", "Portuguese": "pt", "Russian": "ru", "Spanish": "es", "Swedish": "sv"
    }

    FOUNDATIONAL_MODELS = frozenset([
        "claude-4-sonnet", "claude-3-7-sonnet", "llama4-maverick", "llama4-scout",
        "deepseek-r1", "snowflake-arctic", "mistral-large2", "reka-flash",
        "reka-core", "llama3.1-405b", "llama3.2-1b", "llama3.2-3b", "mistral-7b"
    ])

    MULTIMODAL_MODELS = frozenset([
        "pixtral-large", "claude-3-7-sonnet", "claude-4-sonnet", "claude-4-opus"
    ])

    EMAIL_MODELS = frozenset([
        "claude-4-sonnet", "claude-3-7-sonnet", "snowflake-arctic",
        "llama4-maverick", "llama4-scout", "deepseek-r1", "mistral-large",
        "reka-flash", "reka-core", "llama3.1-405b"
    ])

    QA_MODELS = frozenset([
        "claude-4-sonnet", "claude-3-7-sonnet", "snowflake-arctic",
        "llama4-maverick", "llama4-scout", "deepseek-r1", "mistral-large2",
        "reka-flash", "reka-core", "mixtral-8x7b"
    ])

    PREVIEWABLE_EXTENSIONS = frozenset(['.txt', '.tsv', '.csv', '.jpg', '.img', '.webp', '.jpeg', '.mp3'])

    # Improved regex patterns for validation
    STAGE_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9_]{1,50}$')
    FILENAME_PATTERN = re.compile(r'^[a-zA-Z0-9._\-\s]{1,255}$')

    # File size limits
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_AUDIO_SIZE = 25 * 1024 * 1024  # 25MB

    def __init__(self):
        self.session = None
        self._initialize_session()

    def _initialize_session(self) -> None:
        """Safely initialize Snowflake session with error handling"""
        try:
            self.session = get_active_session()
            logger.info("Snowflake session initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Snowflake session: {str(e)}")
            st.error("Failed to connect to Snowflake. Please check your connection.")
            st.stop()

    @staticmethod
    def sanitize_input(text: str, max_length: int = 50000) -> str:
        """Enhanced input sanitization with length limits"""
        if not isinstance(text, str):
            return ""

        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length]

        # HTML escape and normalize whitespace
        sanitized = html.escape(text.strip())
        return sanitized

    @classmethod
    def validate_stage_name(cls, stage_name: str) -> bool:
        """Validate stage name using regex for better performance"""
        if not stage_name or not isinstance(stage_name, str):
            return False
        return bool(cls.STAGE_NAME_PATTERN.match(stage_name))

    @classmethod
    def validate_model_name(cls, model_name: str, allowed_models: frozenset) -> bool:
        """Validate model name against allowed set"""
        return model_name in allowed_models

    @classmethod
    def validate_filename(cls, filename: str) -> bool:
        """Validate filename with improved pattern matching"""
        if not filename or not isinstance(filename, str):
            return False
        return bool(cls.FILENAME_PATTERN.match(filename))

    @classmethod
    def validate_file_size(cls, file_size: int, file_type: str) -> bool:
        """Validate file size based on type"""
        if file_type in ['jpg', 'jpeg', 'png', 'webp', 'pdf']:
            return file_size <= cls.MAX_IMAGE_SIZE
        elif file_type in ['mp3', 'wav', 'm4a', 'flac']:
            return file_size <= cls.MAX_AUDIO_SIZE
        return file_size <= cls.MAX_IMAGE_SIZE  # Default limit

    def execute_safe_sql(self, query: str, params: Optional[List[Any]] = None) -> Optional[pd.DataFrame]:
        """Execute SQL with enhanced error handling and logging"""
        try:
            # Log query without sensitive parameters
            logger.info(f"Executing SQL query: {query[:100]}...")

            if params:
                result = self.session.sql(query, params).to_pandas()
            else:
                result = self.session.sql(query).to_pandas()

            logger.info(f"Query executed successfully, returned {len(result)} rows")
            return result

        except Exception as e:
            logger.error(f"SQL execution error: {str(e)}")
            st.error("An error occurred while processing your request. Please try again.")
            return None

    def ensure_stage_exists(self, stage_name_no_at: str) -> bool:
        """Creates a Snowflake stage if it doesn't exist with enhanced validation"""
        if not self.validate_stage_name(stage_name_no_at):
            st.sidebar.error("Invalid stage name. Use only alphanumeric characters and underscores (1-50 chars).")
            return False

        try:
            # Check if stage exists
            self.session.sql(f"DESC STAGE {stage_name_no_at}").collect()
            return True
        except:
            # Create stage if it doesn't exist
            try:
                self.session.sql(f"""
                    CREATE STAGE IF NOT EXISTS {stage_name_no_at}
                    ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE')
                """).collect()
                st.sidebar.success(f"Stage @{stage_name_no_at} has been created.")
                return True
            except Exception as e:
                logger.error(f"Failed to create stage: {str(e)}")
                st.sidebar.error(f"Failed to create stage: {str(e)}")
                return False


# Initialize the secure app - using singleton pattern for better performance
@st.cache_resource
def get_app_instance():
    return SecureSnowflakeApp()

app = get_app_instance()


# Optimized CSS styling
def load_custom_css():
    """Load custom CSS with improved security"""
    css = """
    <style type="text/css">
    [data-testid=stSidebar] {
        background-color: rgb(50, 50, 130);
        color: #FFFFFF;
    }
    .card-style {
        border: 1px groove #52546a;
        border-radius: 10px;
        padding: 25px;
        box-shadow: -6px 8px 20px 1px #00000052;
    }
    audio::-webkit-media-controls-panel,
    audio::-webkit-media-controls-enclosure {
        background-color: #9c9d9f;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

load_custom_css()

def read_svg(path: str) -> Optional[str]:
    """Safely read SVG files with enhanced error handling"""
    try:
        svg_path = Path(path)
        if not svg_path.exists() or not svg_path.is_file():
            logger.warning(f"SVG file not found: {path}")
            return None

        # Additional security check for file extension
        if svg_path.suffix.lower() != '.svg':
            logger.warning(f"File is not an SVG: {path}")
            return None

        with open(svg_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Basic SVG validation
            if not content.strip().startswith('<svg'):
                logger.warning(f"Invalid SVG content in file: {path}")
                return None
            return content

    except Exception as e:
        logger.error(f"Error reading SVG file {path}: {str(e)}")
        return None

def create_card_container(content_func):
    """Helper function to create consistent card styling"""
    with stylable_container(
        "Card1",
        css_styles="border: 1px groove #52546a; border-radius: 10px; padding: 25px; box-shadow: -6px 8px 20px 1px #00000052;"
    ):
        content_func()

def toolsapp():
    """Display the welcome page with logos and header information"""
    with st.container():
        svg_content = read_svg("Snowflake.svg")

        cl1, cl2 = st.columns([5, 1])

        with cl1:
            create_card_container(lambda: st.write(" "))
            st.title("Unlock Insights from Unstructured Data with Snowflake Cortex AI")

            st.metric(
                " ",
                "Snowflake Summit HOL: AI209",
                help="The Best HOL Today!"
            )
            st.divider()
            st.subheader("Welcome to Your New Generative AI Tools App!")
            st.divider()
            create_card_container(lambda: st.write(" "))

        with cl2:
            if svg_content:
                st.image(svg_content, width=75)


def translate():
    """Translation functionality using Snowflake Cortex AI"""
    with st.container():
        st.header("Translate With Snowflake Cortex")

        col1, col2 = st.columns(2)
        with col1:
            from_language = st.selectbox(
                "From",
                options=list(app.SUPPORTED_LANGUAGES.keys()),
                index=list(app.SUPPORTED_LANGUAGES.keys()).index("English")
            )
        with col2:
            to_language = st.selectbox(
                "To",
                options=list(app.SUPPORTED_LANGUAGES.keys()),
                index=list(app.SUPPORTED_LANGUAGES.keys()).index("Spanish")
            )

        xlate_entered_text = st.text_area(
            "Enter text",
            label_visibility="hidden",
            height=300,
            placeholder="For example: call transcript",
            max_chars=5000
        )

        if xlate_entered_text:
            sanitized_text = app.sanitize_input(xlate_entered_text, 5000)
            query = "SELECT snowflake.cortex.translate(?, ?, ?) as response"
            params = [
                sanitized_text,
                app.SUPPORTED_LANGUAGES[from_language],
                app.SUPPORTED_LANGUAGES[to_language]
            ]

            result = app.execute_safe_sql(query, params)
            if result is not None and not result.empty:
                st.write(result.iloc[0]["RESPONSE"])

def sentiment():
    """Sentiment analysis functionality using Snowflake Cortex AI"""
    with st.container():

        st.header("Sentiment Analysis With Snowflake Cortex")

        sent_entered_transcript = st.text_area(
            "Enter call transcript",
            label_visibility="hidden",
            height=400,
            placeholder="Enter call transcript",
            max_chars=10000
        )

        if sent_entered_transcript:
            sanitized_text = app.sanitize_input(sent_entered_transcript, 10000)
            query = "SELECT snowflake.cortex.sentiment(?) as sentiment"
            params = [sanitized_text]

            result = app.execute_safe_sql(query, params)
            if result is not None and not result.empty:
                st.caption("Score is between -1 and 1; -1 = Most negative, 1 = Positive, 0 = Neutral")
                st.dataframe(result, hide_index=True, width=100)

def supersum():
    """Text summarization functionality using Snowflake Cortex AI"""
    with st.container():

        st.header("Summarize Data With Snowflake Cortex")

        ssum_entered_text = st.text_area(
            "Enter data to summarize",
            label_visibility="hidden",
            height=400,
            placeholder="Enter data to summarize",
            max_chars=15000
        )

        if ssum_entered_text:
            sanitized_text = app.sanitize_input(ssum_entered_text, 15000)
            query = "SELECT snowflake.cortex.summarize(?) as RESPONSE"
            params = [sanitized_text]

            result = app.execute_safe_sql(query, params)
            if result is not None and not result.empty:
                st.caption("Summarized data:")
                st.write(result.iloc[0]["RESPONSE"])

def nextba():
    """Next Best Action recommendation using Snowflake foundational LLMs"""
    with st.container():

        st.header("Use a Snowflake Foundational LLM to Identify Customer Next Best Action")

        next_selected_model = st.selectbox(
            "Which Foundational Model:",
            options=list(app.FOUNDATIONAL_MODELS)
        )

        next_entered_code = st.text_area(
            "Paste the Data for Your Question",
            label_visibility="hidden",
            height=300,
            placeholder="Paste Data",
            max_chars=10000
        )

        next_default_model_instruct = "Based on these comments, please provide a recommended next best action"

        next_model_instruct = st.text_area(
            "Please provide Model Instructions",
            next_default_model_instruct,
            label_visibility="hidden",
            placeholder="Enter Prompt",
            max_chars=2000
        )

        if st.button("Next Best Action!"):
            if app.validate_model_name(next_selected_model, app.FOUNDATIONAL_MODELS):
                sanitized_code = app.sanitize_input(next_entered_code, 10000)
                sanitized_instruct = app.sanitize_input(next_model_instruct, 2000)

                full_prompt = f"[INST]{sanitized_instruct}{sanitized_code}[/INST]"
                query = f"SELECT snowflake.cortex.complete('{next_selected_model}', ?) AS RESPONSE"
                params = [full_prompt]

                result = app.execute_safe_sql(query, params)
                if result is not None and not result.empty:
                    st.caption("Answer:")
                    st.write(result.iloc[0]["RESPONSE"])

def classify():
    """Text classification functionality using Snowflake Cortex AI"""
    with st.container():

        st.header("Classify Data With Snowflake Cortex")

        class_entered_text = st.text_area(
            "Enter data to Classify",
            label_visibility="hidden",
            height=400,
            placeholder="Enter data to classify",
            max_chars=10000
        )

        if class_entered_text:
            sanitized_text = app.sanitize_input(class_entered_text, 10000)
            categories = [
                'Complete Refund', 'Exchange Tickets', 'Refund Fees',
                'Discount Sale', 'Send a Nice Thank You E-mail', 'No Category'
            ]

            # Safely construct JSON string
            json_categories_string_literal = json.dumps(categories)
            query = f"SELECT snowflake.cortex.ai_classify(?, PARSE_JSON('{json_categories_string_literal}')) as Answer"
            params = [sanitized_text]

            result = app.execute_safe_sql(query, params)
            if result is not None and not result.empty:
                st.caption("Classified data:")
                st.write(result.iloc[0]["ANSWER"])

def emailcomplete():
    """Email generation functionality using Snowflake foundational LLMs"""
    with st.container():

        st.header("Generate a Customer E-Mail With Snowflake Cortex Complete")

        email_selected_model = st.selectbox(
            "Which Foundational Model:",
            options=list(app.EMAIL_MODELS)
        )

        email_entered_code = st.text_area(
            "Paste the Call Transcript to use for E-Mail Generation:",
            label_visibility="hidden",
            height=300,
            placeholder="Paste Call Transcript",
            max_chars=10000
        )

        email_default_model_instruct = """Please create an email for me that describes the issue in detail and provides a solution. Make the e-mail from me, the Director of Customer Relations at The Big Ticket Co, and also give the customer a 10% discount with code: CS10OFF of a future order"""

        email_model_instruct = st.text_area(
            "Please Provide E-Mail Generation Model Instructions: ",
            email_default_model_instruct,
            label_visibility="hidden",
            placeholder="Enter Prompt",
            max_chars=2000
        )

        if st.button("Generate E-Mail"):
            if app.validate_model_name(email_selected_model, app.EMAIL_MODELS):
                sanitized_code = app.sanitize_input(email_entered_code, 10000)
                sanitized_instruct = app.sanitize_input(email_model_instruct, 2000)

                full_prompt = f"[INST]{sanitized_instruct}{sanitized_code}[/INST]"
                query = f"SELECT snowflake.cortex.complete('{email_selected_model}', ?) AS RESPONSE"
                params = [full_prompt]

                result = app.execute_safe_sql(query, params)
                if result is not None and not result.empty:
                    st.caption("Customer E-Mail:")
                    st.write(result.iloc[0]["RESPONSE"])

def askaquestion():
    """General question-answering functionality using Snowflake foundational LLMs"""
    with st.container():

        st.header("Use a Snowflake Foundational LLM to Ask a Question")

        askq_selected_model = st.selectbox(
            "Which Foundational Model:",
            options=list(app.QA_MODELS)
        )

        askq_entered_code = st.text_area(
            "Paste the Data for Your Question",
            label_visibility="hidden",
            height=300,
            placeholder="Paste Data",
            max_chars=30000
        )

        askq_model_instruct = st.text_area(
            "Please provide Model Instructions",
            label_visibility="hidden",
            placeholder="Enter Prompt",
            max_chars=2000
        )

        if st.button("Ask My Question!"):
            if app.validate_model_name(askq_selected_model, app.QA_MODELS):
                sanitized_code = app.sanitize_input(askq_entered_code, 30000)
                sanitized_instruct = app.sanitize_input(askq_model_instruct, 2000)

                full_prompt = f"[INST]{sanitized_instruct}{sanitized_code}[/INST]"
                query = f"SELECT snowflake.cortex.complete('{askq_selected_model}', ?) AS RESPONSE"
                params = [full_prompt]

                result = app.execute_safe_sql(query, params)
                if result is not None and not result.empty:
                    st.caption("Answer:")
                    st.write(result.iloc[0]["RESPONSE"])

def handle_file_upload(uploaded_file, stage_name: str, file_type: str) -> bool:
    """Centralized file upload handling with validation"""
    # Validate file size
    if not app.validate_file_size(uploaded_file.size, file_type):
        max_size = app.MAX_AUDIO_SIZE if file_type in ['mp3', 'wav', 'm4a', 'flac'] else app.MAX_IMAGE_SIZE
        st.error(f"File size too large. Maximum size is {max_size // (1024*1024)}MB.")
        return False

    # Validate filename
    if not app.validate_filename(uploaded_file.name):
        st.error("Invalid file name. Use only alphanumeric characters, dots, underscores, hyphens, and spaces.")
        return False

    try:
        file_stream = io.BytesIO(uploaded_file.getvalue())
        app.session.file.put_stream(
            file_stream,
            f"{stage_name}/{uploaded_file.name}",
            auto_compress=False,
            overwrite=True
        )
        st.success(f"File '{uploaded_file.name}' has been uploaded successfully!")
        return True
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        st.error("Error occurred while uploading file.")
        return False

def mmimage():
    #"""Multi-modal image analysis functionality using Snowflake Cortex AI"""
    st.title("Multi-Modal Image Categorizer")

    st.header("Stage Settings")
    stage_name_no_at = st.text_input(
        "Enter stage name (e.g., GENAI_STAGE)",
        "GENAI_STAGE",
        max_chars=50
    )

    if not app.ensure_stage_exists(stage_name_no_at):
        return

    stage_name = f"@{stage_name_no_at}"

    st.header("File Upload")
    st.write("Upload files to Snowflake stage.")

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['jpg', 'jpeg', 'png', 'webp', 'pdf']
    )

    if uploaded_file:
        file_extension = Path(uploaded_file.name).suffix.lower()

        if handle_file_upload(uploaded_file, stage_name, file_extension[1:]):
            image_selected_model = st.selectbox(
                "Which Multi-Modal Model:",
                options=list(app.MULTIMODAL_MODELS)
            )

            image_default_model_instruct = """Please provide the type of animal, breed, and environment in JSON format:
            Animal: ??,
            Breed: ??,
            Environment: ??"""

            image_model_instruct = st.text_area(
                "Please Provide Model Instructions: ",
                image_default_model_instruct,
                placeholder="Enter Prompt",
                height=150,
                max_chars=2000
            )

            if st.button("Image Details"):
                if app.validate_model_name(image_selected_model, app.MULTIMODAL_MODELS):
                    sanitized_instruct = app.sanitize_input(image_model_instruct, 2000)
                    # Escape filename for SQL
                    escaped_filename = uploaded_file.name.replace("'", "''")
                    query = f"SELECT snowflake.cortex.complete('{image_selected_model}', ?, TO_FILE('{stage_name}', '{escaped_filename}')) as RESPONSE"
                    params = [sanitized_instruct]

                    result = app.execute_safe_sql(query, params)
                    if result is not None and not result.empty:
                        st.write(result.iloc[0]["RESPONSE"])

            # Preview uploaded file
            if file_extension in app.PREVIEWABLE_EXTENSIONS:
                try:
                    uploaded_file.seek(0)
                    if file_extension in ['.webp', '.jpg', '.jpeg', '.png', '.img']:
                        st.image(uploaded_file)
                    elif file_extension == '.pdf':
                        st.write("PDF file uploaded successfully. Preview not available.")
                    else:
                        # Handle CSV/TSV files
                        try:
                            df_preview = pd.read_csv(uploaded_file, sep='\t', nrows=100)
                            st.write("Preview of uploaded data:")
                            st.dataframe(df_preview.head())
                        except Exception:
                            uploaded_file.seek(0)
                            df_preview = pd.read_csv(uploaded_file, sep='\t', encoding='shift-jis', nrows=100)
                            st.write("Preview of uploaded data:")
                            st.dataframe(df_preview.head())

                except Exception as e:
                    logger.error(f"Error previewing file: {str(e)}")
                    st.error("Error occurred while previewing file.")

def mmaudio():
    #"""Audio transcription functionality using Snowflake AI"""
    st.title("Audio Transcription")

    st.header("Stage Settings")
    stage_name_no_at = st.text_input(
        "Enter stage name (e.g., GENAI_AUDIO_STAGE)",
        "GENAI_AUDIO_STAGE",
        max_chars=50
    )

    if not app.ensure_stage_exists(stage_name_no_at):
        return

    stage_name = f"@{stage_name_no_at}"

    st.header("File Upload")
    st.write("Upload files to Snowflake stage.")

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['mp3', 'wav', 'm4a', 'flac']
    )

    if uploaded_file:
        file_extension = Path(uploaded_file.name).suffix.lower()

        if handle_file_upload(uploaded_file, stage_name, file_extension[1:]):
            audio_input = f"{stage_name}/{uploaded_file.name}"

            try:
                aud = app.session.file.get_stream(audio_input)
                st.audio(aud, format='audio/mpeg')
            except Exception as e:
                logger.warning(f"Could not display audio player: {str(e)}")

            # Escape filename for SQL
            escaped_file_name = uploaded_file.name.replace("'", "''")
            query = f"SELECT AI_TRANSCRIBE(TO_FILE('{stage_name}/{escaped_file_name}')) as RESPONSE"

            result = app.execute_safe_sql(query)
            if result is not None and not result.empty:
                st.write(result.iloc[0]["RESPONSE"])

# Navigation dictionary - all original functionality preserved
PAGE_FUNCTIONS = {
    "Tools App": toolsapp,
    "Transcribe (PrPr)": mmaudio,
    "Translation": translate,
    "Sentiment Analysis": sentiment,
    "Summarize": supersum,
    "Classify": classify,
    "Next Best Action": nextba,
    "Generate E-Mail": emailcomplete,
    "Ask a Question": askaquestion,
    "Image Analysis": mmimage
}

def main():
    """Main application entry point"""
    # Sidebar navigation
    svg_content = read_svg("Snowflake_Logo.svg")
    if svg_content:
        st.sidebar.image(svg_content, width=150)
    selected_page = st.sidebar.selectbox("", list(PAGE_FUNCTIONS.keys()))

    # Execute the selected page function with error handling
    try:
        PAGE_FUNCTIONS[selected_page]()
    except Exception as e:
        logger.error(f"Error executing page function '{selected_page}': {str(e)}")
        st.error("An unexpected error occurred. Please try again or contact support.")

if __name__ == "__main__":
    main()
