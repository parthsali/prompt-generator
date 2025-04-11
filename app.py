import streamlit as st
import os
from PIL import Image
import tempfile
import json
from google import genai
import re

# Set page configuration
st.set_page_config(
    page_title="Technical Question Analyzer",
    page_icon="📸",
    layout="wide"
)

# Initialize Google AI client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Create a temporary directory to store uploaded images
if 'temp_dir' not in st.session_state:
    st.session_state.temp_dir = tempfile.mkdtemp()
    
# Ensure the temporary directory exists
os.makedirs(st.session_state.temp_dir, exist_ok=True)

def create_llm_prompt(json_data):
    """
    Create a comprehensive prompt for the LLM using the JSON data
    """
    prompt_template = """You're an expert problem solver and programmer. Think deeply and act like you're solving a real-world problem in a coding interview or a competitive programming contest.

You are given a problem described in the JSON format below. Your task is to **understand the problem** from this structured data and generate a **detailed, human-readable version of the question**, clearly explaining:

1. The **type of question** (e.g., coding, MCQ, run-code),
2. The **problem statement** in a clean and easy-to-read way,
3. The **function signature or expected output** if applicable,
4. The **constraints, input and output formats**, and
5. Any **examples/test cases** if given.

Use the information in the JSON as your only source. Be precise, concise, and clear. Think like someone preparing the problem for a coding platform or exam.

Here is the JSON:


{json_data}


Now, give me working solution for this problem, for coding if language is given, else give me solution in c++"""

    return prompt_template.format(json_data=json_data)

def extract_question_number(text):
    """
    Extract question number from text using various patterns
    """
    patterns = [
        r'Q(?:uestion)?\s*\.?\s*(\d+[a-z]?)',  # Matches Q1, Question 1, Q.1, Q1a
        r'(?:^|\s)(\d+[a-z]?)[\.\)]',          # Matches 1., 1), 1a.
        r'(?:^|\s)([a-z][\.\)])(?:\s|$)',      # Matches a., a), b.
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return None

def process_image(image_path):
    """
    Process the image and generate comprehensive analysis
    """
    initial_prompt = '''
    Analyze the provided image content, which contains a technical or aptitude question. First, determine the question type from the options: "mcq", "run-code", "coding", or "unknown". Then, extract the relevant information and format it *strictly* as a JSON object according to the structure defined below for the determined type. Infer 'subject' (e.g., OS, DBMS, Java, Aptitude) and 'language' (e.g., Java, C++, Python, C) where possible from the context.
    If you can identify a question number (e.g., Q1, Question 2, etc.), include it in the response.
    
    **JSON Output Formats:**
    ... (keep existing JSON formats) ...
    '''

    try:
        # Generate the response
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[
                initial_prompt,
                Image.open(image_path)
            ]
        )
        
        json_data = response.text
        
        # Create the LLM prompt using the JSON data
        llm_prompt = create_llm_prompt(json_data)
        
        return {
            "llm_prompt": llm_prompt
        }
    except Exception as e:
        error_json = json.dumps({"type": "unknown", "error": str(e)})
        return {
            "structured_data": error_json,
            "llm_prompt": create_llm_prompt(error_json)
        }

def main():
    st.title("📸 Technical Question Analyzer")
    st.write("Upload your technical question images and get structured analysis prompts!")

    # File uploader
    uploaded_files = st.file_uploader(
        "Choose photos to upload",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True
    )

    if uploaded_files:
        st.write(f"Number of photos uploaded: {len(uploaded_files)}")
        
        # Process each uploaded file
        for uploaded_file in uploaded_files:
            # Create columns for image and analysis
            col1, col2 = st.columns([1, 2])
            
            # Save the uploaded file temporarily
            temp_path = os.path.join(st.session_state.temp_dir, uploaded_file.name)
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Try to extract question number from the image
            result = process_image(temp_path)
            question_id = None
            try:
                data = json.loads(result["structured_data"])
                extracted_number = extract_question_number(data.get('question_text', '') or data.get('raw_text', ''))
                if extracted_number:
                    question_id = f"Q{extracted_number}"
            except:
                pass
            
            # Display image
            with col1:
                if question_id:
                    st.subheader(question_id)
                st.image(temp_path, caption=uploaded_file.name, use_column_width=True)
            
            # Display analysis
            with col2:
                # Display LLM prompt
                st.subheader("LLM Prompt")
                st.text_area("Complete Prompt for LLM:", result["llm_prompt"], height=300, key=f"prompt_{uploaded_file.name}")
            
            st.divider()
            
            # Clean up: remove the temporary file
            try:
                os.remove(temp_path)
            except Exception as e:
                st.warning(f"Could not remove temporary file: {e}")

    # Clean up temporary directory when session ends
    if st.session_state.temp_dir and os.path.exists(st.session_state.temp_dir):
        try:
            for file in os.listdir(st.session_state.temp_dir):
                file_path = os.path.join(st.session_state.temp_dir, file)
                try:
                    os.remove(file_path)
                except Exception:
                    pass
            os.rmdir(st.session_state.temp_dir)
        except Exception as e:
            st.warning(f"Could not clean up temporary directory: {e}")

if __name__ == "__main__":
    main()