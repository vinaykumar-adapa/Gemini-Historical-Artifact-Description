import streamlit as st
import google.generativeai as genai
import os
import random
from PIL import Image
from dotenv import load_dotenv

# 1. Configuration & API Setup
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

historical_facts = [
    "The Great Pyramid of Giza was the tallest man-made structure for over 3,800 years.",
    "Renaissance means 'rebirth' in French, marking a bridge to modern history.",
    "Tutankhamun's tomb was discovered in 1922 by Howard Carter.",
    "The Bayeux Tapestry is nearly 70 meters long and tells a massive story.",
    "Leonardo da Vinci wrote his notes in 'mirror writing' from right to left."
]

if 'run_generation' not in st.session_state:
    st.session_state.run_generation = False

def trigger_generation():
    st.session_state.run_generation = True

# 3. Logic: Handles Text-only, Image-only, or Both
def generate_artifact_description(name, period, count, image_file=None):
    model = genai.GenerativeModel('gemini-flash-latest')
    period_info = f"from the {period} era" if period else ""
    subject = name if name else "the artifact shown in this image"
    
    prompt = f"""
    You are a friendly Museum Guide. 
    Write a detailed story about: {subject} {period_info}.
    Target Length: {count} words.

    RULES:
    1. DO NOT include greetings (No 'Hello', 'Welcome').
    2. If an image is provided but no name is given, identify the artifact first.
    3. Use simple English and clear, short headings.
    4. Write in long, detailed paragraphs to reach the {count} word goal.
    """
    
    if image_file:
        img = Image.open(image_file)
        response = model.generate_content([prompt, img])
    else:
        response = model.generate_content(prompt)
    return response.text

# 4. Museum UI Design
st.set_page_config(page_title="Gemini Artifact Explorer", page_icon="🏛️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F2F2F2; }
    section[data-testid="stSidebar"] { background-color: #1B1B1B !important; color: #D9B061 !important; }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] label { color: #D9B061 !important; }
    .stButton>button { background-color: #D9B061 !important; color: #1B1B1B !important; font-weight: bold; border: 2px solid #1B1B1B; }
    .report-text { color: #1B1B1B; font-size: 1.15rem; background-color: white; padding: 30px; border-radius: 10px; border-left: 5px solid #D9B061; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); white-space: pre-wrap; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.image("https://img.icons8.com/color/96/museum.png")
    st.title("WELCOME TO GEMINI ARTIFACTS")
    artifact_name = st.text_input("Enter artifact name?", placeholder="e.g. The Rosetta Stone")
    historical_period = st.text_input("Which time period? (Optional)", placeholder="e.g. Ancient Egypt")
    word_count = st.select_slider("Desired word count?", options=[100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1200, 1500, 2000], value=800)
    st.divider()
    if st.button("Generate Description"):
        st.session_state.run_generation = True

st.title("🏛️ Gemini Historical Artifact Description")
st.divider()

img_uploaded = st.session_state.get('main_upload', None)

if st.session_state.run_generation and (artifact_name or img_uploaded):
    selected_fact = random.choice(historical_facts)
    with st.spinner(f"🏺 Researching... \n\n **Did you know?** {selected_fact}"):
        try:
            description = generate_artifact_description(artifact_name, historical_period, word_count, img_uploaded)
            
            if img_uploaded:
                st.image(img_uploaded, caption="Analyzing Uploaded Artifact", width=400)
            
            display_title = artifact_name if artifact_name else "Historical Discovery"
            st.header(f"The History of {display_title}")
            
            # Displaying the text
            st.markdown(f'<div class="report-text">{description}</div>', unsafe_allow_html=True)
            
            # --- NEW: COPY AND SHARE OPTIONS ---
            st.divider()
            col_a, col_b = st.columns([1, 4])
            
            with col_a:
                # Download button serves as the "Share/Export" feature
                st.download_button(
                    label="💾 Export as Text",
                    data=description,
                    file_name=f"{display_title}_history.txt",
                    #mime="text/plain"
                )
            
            with col_b:
                # Code block for easy "one-click copy"
                st.info("💡 You can copy the text using the icon at the top-right of the box below:")
                st.code(description, language=None)
            
            st.session_state.run_generation = False
        except Exception as e:
            st.error(f"Error: {e}")
            st.session_state.run_generation = False
else:
    st.subheader("Welcome to the Digital Museum")
    st.write("Enter an artifact name or upload a photo to begin.")
    
    col1, col2 = st.columns([1, 2], vertical_alignment="bottom")
    with col1:
        st.button("✨ Start Artifact Research", on_click=trigger_generation)
    with col2:
        st.session_state.main_upload = st.file_uploader("Upload an image (Optional)", type=["jpg", "jpeg", "png"], key="main_upload_widget")