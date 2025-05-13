# Import required libraries
import streamlit as st
import pandas as pd
import os
import io
from snowflake.snowpark.context import get_active_session

# Constants
images_stage = "images_stage"

model_list = [
    "claude-3-5-sonnet",
    "snowflake-arctic",
    'llama4-maverick',
    'llama4-scout',
    "deepseek-r1",
    "mistral-large","mistral-large2","mistral-7b","mixtral-8x7b",
    "reka-flash","reka-core",
    "jamba-instruct","jamba-1.5-mini","jamba-1.5-large",
    "gemma-7b"
]

supported_languages = {
    "Chinese": "zh",
    "Dutch": "nl",
    "English": "en",
    "French": "fr",
    "German": "de",
    "Hindi": "hi",
    "Italian": "it",
    "Japanese": "ja",
    "Korean": "ko",
    "Polish": "pl",
    "Portuguese": "pt",
    "Russian": "ru",
    "Spanish": "es",
    "Swedish": "sv"
}

# Configure Streamlit page layout
st.set_page_config(layout="wide")

st.header("Unlock Insights from Unstructured Data with Snowflake Cortex AI ❄️")

# Initialize Snowflake session
session = get_active_session()

def toolsapp():
    st.subheader("Unlock Insights from Unstructured Data with Snowflake Cortex AI ❄️")
    st.write("Overview")
    st.caption("""This application provides a user-friendly interface to interact with Snowflake's Generative AI capabilities through Streamlit. It leverages Snowflake Cortex and various LLM models to demonstrate different AI functionalities such as translation, sentiment analysis, data summarization, text classification, and more.""")

def translate():
    with st.container():
        st.header("Translate With Snowflake Cortex")
        
        col1, col2 = st.columns(2)
        with col1:
            from_language = st.selectbox("From", dict(supported_languages.items()),index=list(supported_languages.keys()).index("German"))
        with col2:
            to_language = st.selectbox("To", dict(supported_languages.items()),index=list(supported_languages.keys()).index("English"))
        
        entered_text = st.text_area("Enter text",label_visibility="hidden",height=300,
            placeholder="For example: call transcript",)
        if entered_text:
            entered_text = entered_text.replace("'", "\\'")
            cortex_response = (
                session.sql(
                    f"SELECT SNOWFLAKE.CORTEX.TRANSLATE('{entered_text}','{supported_languages[from_language]}','{supported_languages[to_language]}') as RESPONSE;"
                ).to_pandas().iloc[0]["RESPONSE"]
            )
            st.write(cortex_response)

def sentiment():
    with st.container():
        st.header("Sentiment Analysis With Snowflake Cortex")
        
        entered_transcript = st.text_area(
            "Enter call transcript",
            label_visibility="hidden",
            height=300,
            placeholder="Enter call transcript",
        )
        entered_transcript = entered_transcript.replace("'", "\\'")
        
        if entered_transcript:
            cortex_response = session.sql(
                f"SELECT SNOWFLAKE.CORTEX.SENTIMENT('{entered_transcript}') AS sentiment"
            ).to_pandas()
            st.caption("Score is between -1 and 1; -1 = Most negative, 1 = Positive, 0 = Neutral")
            st.dataframe(cortex_response, hide_index=True, width=100)

def supersum():
    with st.container():
        st.header("Summarize Data With Snowflake Cortex")
        entered_text = st.text_area(
            "Enter data to summarize",
            label_visibility="hidden",
            height=300,
            placeholder="Enter data to summarize",
        )
        entered_text = entered_text.replace("'", "\\'")
        
        if entered_text:
            cortex_response = session.sql(
                f"SELECT SNOWFLAKE.CORTEX.SUMMARIZE('{entered_text}') as RESPONSE"
            ).to_pandas().iloc[0]["RESPONSE"];
            st.caption("Summarized data:")
            st.write(cortex_response)

def nextba():
    with st.container():
        st.header("Use a Snowflake Foundational LLM to Identify Customer Next Best Action")
        
        selected_model = st.selectbox("Which Foundational Model:", model_list)
        
        entered_code = st.text_area("Paste the Data for Your Question",label_visibility="hidden",height=300,placeholder="Paste Data",)
        entered_code = entered_code.replace("'", "\\'")
        
        default_model_instruct = """Based on these data, please provide the next best action"""
        model_instruct = st.text_area("Please provide Model Instructions",default_model_instruct,label_visibility="hidden",placeholder="Enter Prompt",)

        if st.button("Next Best Action!"):
            cortex_response = session.sql(
                    f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{selected_model}',concat('[INST]','{model_instruct}','{entered_code}','[/INST]')) as RESPONSE"
            ).to_pandas().iloc[0]["RESPONSE"]
            
            st.caption("Answer:")
            st.write(cortex_response)

def classify():
    with st.container():
        st.header("Classify Data With Snowflake Cortex")
        
        entered_text = st.text_area("Enter data to Classify",label_visibility="hidden",height=300,placeholder="Enter data to classify",)
        entered_text = entered_text.replace("'", "\\'")

        if entered_text:
            cortex_response = session.sql(
                f"select snowflake.cortex.classify_text('{entered_text}',['Refund','Exchange','No Category']) as Answer"
            ).to_pandas().iloc[0]["ANSWER"];
            
            st.caption("Classified data:")
            st.write(cortex_response)

def emailcomplete():
    with st.container():
        st.header("Generate a Customer E-Mail With Snowflake Cortex Complete")
        
        selected_model = st.selectbox("Which Foundational Model:", model_list)
        
        entered_code = st.text_area("Paste the Call Transcript to use for E-Mail Generation:",label_visibility="hidden",height=300,placeholder="Paste Call Transcript",)
        entered_code = entered_code.replace("'", "\\'")
        
        default_model_instruct = """Please create an email for me that describes the issue in detail and provides a solution. Make the e-mail from me, the Director of Customer Relations at Ski Gear Co, and also give the customer a 10% discount with code: CS10OFF"""
        
        model_instruct = st.text_area("Please Provide E-Mail Generation Model Instructions: ",default_model_instruct,label_visibility="hidden",placeholder="Enter Prompt",)

        if st.button("Generate E-Mail"):
            cortex_response = session.sql(
                f"select snowflake.cortex.complete('{selected_model}',concat('[INST]','{model_instruct}','{entered_code}','[/INST]')) as RESPONSE").to_pandas().iloc[0]["RESPONSE"];
            
            st.caption("Customer E-Mail:")
            st.write(cortex_response)

def askaquestion():
    with st.container():
        st.header("Use a Snowflake Foundational LLM to Ask a Question")
        
        selected_model = st.selectbox("Which Foundational Model:", model_list)
        entered_code = st.text_area(
            "Paste the Data for Your Question",
            label_visibility="hidden",
            height=300,
            placeholder="Paste Data",
        )
        entered_code = entered_code.replace("'", "\\'")
        model_instruct = st.text_area(
            "Please provide Model Instructions",
            label_visibility="hidden",
            placeholder="Enter Prompt",
        )

        if st.button("Ask My Question!"):
            cortex_response = session.sql(
                    f"select snowflake.cortex.complete('{selected_model}',concat('[INST]','{model_instruct}','{entered_code}','[/INST]')) as RESPONSE").to_pandas().iloc[0]["RESPONSE"];
            st.caption("Answer:")
            st.write(cortex_response)

def mmimage():
    st.subheader("File Upload")
    st.write("Upload files to Snowflake stage.")

    uploaded_file = st.file_uploader("Choose a file")

    if uploaded_file:
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        try:
            file_stream = io.BytesIO(uploaded_file.getvalue())
            session.file.put_stream(
                file_stream,
                f"{images_stage}/{uploaded_file.name}",
                auto_compress=False,
                overwrite=True
            )
            st.success(f"File '{uploaded_file.name}' has been uploaded successfully!")

            image_file=session.file.get_stream(f'@{images_stage}/{uploaded_file.name}' , decompress=False).read() 
            st.image(image_file, width=300)

            llm_selection = st.selectbox(
                "Select an Large Language Model:",
                options=["claude-3-5-sonnet", "pixtral-large"]
            )
            
            user_prompt = st.text_input("Enter a prompt for the AI model:",value="Please provide a concise description of this image.")

            if st.button("Run AI Model"):
                if user_prompt:
                    image_text = session.sql(f"""
                        SELECT SNOWFLAKE.CORTEX.COMPLETE('{llm_selection}',
                            'Please provide a concise description of this image.',
                            TO_FILE('@{images_stage}', '{uploaded_file.name}')
                        );""").collect()
                    st.write(image_text[0][0])
        
        except Exception as e:
            st.error(f"Error occurred while uploading file: {str(e)}")

# Dictionary mapping page names to their corresponding functions
page_names_to_funcs = {
    "Tools App": toolsapp,
    "Translation": translate,
    "Sentiment Analysis": sentiment,
    "Summarize": supersum,
    "Next Best Action": nextba,
    "Classify": classify,
    "Generate E-Mail": emailcomplete,
    "Ask a Question": askaquestion,
    "Multi-Modal Image Analysis": mmimage
}

# Sidebar navigation
selected_page = st.sidebar.selectbox("Select", page_names_to_funcs.keys())
page_names_to_funcs[selected_page]()
