import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- 1. APP CONFIGURATION ---
st.set_page_config(page_title="ComicVault Pro", layout="wide")

# --- 2. AI SETUP (Gemini) ---
# This looks for the GEMINI_API_KEY in your Streamlit Cloud "Secrets"
api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.warning("⚠️ API Key not found. Please add GEMINI_API_KEY to your Streamlit Secrets.")

# --- 3. SIDEBAR NAVIGATION ---
st.sidebar.title("Menu")
page = st.sidebar.radio("Go to", ["Scan & Add", "My Collection"])

# --- 4. PAGE: SCAN & ADD ---
if page == "Scan & Add":
    st.title("ComicVault Pro")
    st.header("Scan or Add Comic")
    st.markdown("Works for DC, Marvel, Image, Dark Horse, and more.")
    
    picture = st.camera_input("Take photo of comic cover")
    
    if picture:
        # Display the captured image immediately
        img = Image.open(picture)
        st.image(img, caption="Captured photo", width=400)
        
        # Identification Logic
        if st.button("Analyze Comic"):
            if not api_key:
                st.error("Cannot analyze without an API Key in Secrets.")
            else:
                with st.spinner("Searching the Multiverse for this issue..."):
                    try:
                        # This prompt works for DC (Green Lantern), Image, Dark Horse, etc.
                        prompt = """
                        Identify this comic book cover. 
                        Be specific. Find the:
                        1. Publisher (DC, Marvel, Image, Dark Horse, etc.)
                        2. Series Title
                        3. Issue Number
                        4. Notable Story Arc or Characters
                        Return the results clearly.
                        """
                        response = model.generate_content([prompt, img])
                        
                        st.success("Target Identified!")
                        st.markdown(f"### Results:\n{response.text}")
                    except Exception as e:
                        st.error(f"Scanner error: {e}")

        # Manual entry if the AI needs correction
        with st.expander("Edit Details Manually"):
            title = st.text_input("Title", "Green Lantern")
            issue = st.text_input("Issue #", "101")
            grade = st.selectbox("Grade", ["NM", "VF", "FN", "VG", "Good", "Fair", "Poor"])
            if st.button("Save to Vault"):
                st.success(f"Added {title} #{issue} to your collection!")

# --- 5. PAGE: MY COLLECTION ---
elif page == "My Collection":
    st.header("My Collection")
    st.info("Collection database coming soon...")

st.markdown("---")
st.write("Deployed on Streamlit Cloud — Powered by Google Gemini AI")
