import streamlit as st
from PIL import Image
import io
import base64

# Optional imports - handle gracefully if not installed
try:
    import speech_recognition as sr
    speech_recognition_available = True
except ImportError:
    speech_recognition_available = False

try:
    from gtts import gTTS
    gtts_available = True
except ImportError:
    gtts_available = False

try:
    import pytesseract
    # Comment this out if Tesseract is in PATH or use a different path based on your system
    # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    tesseract_available = True
except ImportError:
    tesseract_available = False

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.messages import HumanMessage
    langchain_available = True
except ImportError:
    langchain_available = False

# Function to convert an image to Base64 format
def image_to_base64(image):
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode()

# Function to run OCR on an image
def run_ocr(image):
    if not tesseract_available:
        return "Tesseract OCR is not installed. Please install pytesseract package."
    return pytesseract.image_to_string(image).strip()

# Function to analyze the image using Gemini
def analyze_image(image, prompt):
    if not langchain_available:
        return "LangChain and Google Generative AI packages are not installed. Please install required packages."
    
    try:
        # Replace with your actual API key
        google_api_key = st.text_input("Enter your Google API key", type="password")
        
        if not google_api_key:
            return "Please enter your Google API key to analyze images."
        
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=google_api_key)
        
        image_base64 = image_to_base64(image)
        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": f"data:image/png;base64,{image_base64}"}
            ]
        )
        response = llm.invoke([message])
        return response.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# Function to convert text to speech
def text_to_speech(text):
    if not gtts_available:
        return None
    
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        return audio_bytes.getvalue()
    except Exception as e:
        st.error(f"Text-to-speech error: {str(e)}")
        return None

# Function to recognize speech input
def recognize_speech():
    if not speech_recognition_available:
        return "Speech recognition package is not installed. Please install speech_recognition package."
    
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            st.write("Listening...")
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            return text
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand that."
    except sr.RequestError:
        return "Speech recognition service is unavailable."
    except Exception as e:
        return f"Error: {str(e)}"

# Main app function
def main():
    st.set_page_config(page_title="AI Assistive Tool", layout="wide", page_icon="🤖")
    st.title('AI Assistive Tool for Visually Impaired 👁️ 🤖')
    
    # Check for required packages
    missing_packages = []
    if not speech_recognition_available:
        missing_packages.append("speech_recognition")
    if not gtts_available:
        missing_packages.append("gtts")
    if not tesseract_available:
        missing_packages.append("pytesseract")
    if not langchain_available:
        missing_packages.append("langchain_google_genai")
    
    if missing_packages:
        st.warning(f"Missing packages: {', '.join(missing_packages)}. Install them using pip.")
    
    # API key input - moved to sidebar
    st.sidebar.subheader("Google API Key")
    api_key = st.sidebar.text_input("Enter your Google API key", type="password")
    st.sidebar.info("Your API key is required for image analysis features.")
    
    uploaded_file = st.sidebar.file_uploader("Upload an image (jpg, jpeg, png)", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        
        option = st.radio("Select an action:", ("Describe Scene", "Extract Text", "Detect Objects", "Voice Interaction"))
        
        if option == "Describe Scene":
            if st.button("Analyze Scene"):
                if not api_key:
                    st.error("Please enter your Google API key in the sidebar.")
                else:
                    with st.spinner("Analyzing scene..."):
                        try:
                            llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)
                            image_base64 = image_to_base64(image)
                            message = HumanMessage(
                                content=[
                                    {"type": "text", "text": "Describe this image briefly."},
                                    {"type": "image_url", "image_url": f"data:image/png;base64,{image_base64}"}
                                ]
                            )
                            response = llm.invoke([message])
                            scene_description = response.content.strip()
                            st.success(scene_description)
                            audio_data = text_to_speech(scene_description)
                            if audio_data:
                                st.audio(audio_data, format='audio/mp3')
                        except Exception as e:
                            st.error(f"Error analyzing image: {str(e)}")
        
        elif option == "Extract Text":
            if st.button("Extract Text"):
                with st.spinner("Extracting text..."):
                    extracted_text = run_ocr(image)
                    st.info(extracted_text)
                    audio_data = text_to_speech(extracted_text)
                    if audio_data:
                        st.audio(audio_data, format='audio/mp3')
        
        elif option == "Detect Objects":
            if st.button("Detect Objects"):
                if not api_key:
                    st.error("Please enter your Google API key in the sidebar.")
                else:
                    with st.spinner("Detecting objects..."):
                        try:
                            llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)
                            image_base64 = image_to_base64(image)
                            message = HumanMessage(
                                content=[
                                    {"type": "text", "text": "Identify objects and obstacles."},
                                    {"type": "image_url", "image_url": f"data:image/png;base64,{image_base64}"}
                                ]
                            )
                            response = llm.invoke([message])
                            obstacle_description = response.content.strip()
                            st.success(obstacle_description)
                            audio_data = text_to_speech(obstacle_description)
                            if audio_data:
                                st.audio(audio_data, format='audio/mp3')
                        except Exception as e:
                            st.error(f"Error detecting objects: {str(e)}")
        
        elif option == "Voice Interaction":
            if st.button("Start Voice Recognition"):
                user_query = recognize_speech()
                st.write(f"You said: {user_query}")
                
                if user_query and not user_query.startswith("Error") and not user_query.startswith("Sorry"):
                    if not api_key:
                        st.error("Please enter your Google API key in the sidebar.")
                    else:
                        with st.spinner("Processing your request..."):
                            try:
                                llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)
                                image_base64 = image_to_base64(image)
                                message = HumanMessage(
                                    content=[
                                        {"type": "text", "text": user_query},
                                        {"type": "image_url", "image_url": f"data:image/png;base64,{image_base64}"}
                                    ]
                                )
                                response = llm.invoke([message])
                                response_text = response.content.strip()
                                st.success(response_text)
                                audio_data = text_to_speech(response_text)
                                if audio_data:
                                    st.audio(audio_data, format='audio/mp3')
                            except Exception as e:
                                st.error(f"Error processing request: {str(e)}")
    else:
        st.info("Please upload an image to get started.")
        
    # Add instructions
    with st.sidebar.expander("Instructions"):
        st.write("""
        1. Enter your Google API key in the sidebar
        2. Upload an image using the file uploader
        3. Select one of the following actions:
           - Describe Scene: Get a general description of the image
           - Extract Text: Read any text visible in the image
           - Detect Objects: Identify objects in the image
           - Voice Interaction: Ask questions about the image using your voice
        4. Click the action button to process
        """)

if __name__ == "__main__":
    main()