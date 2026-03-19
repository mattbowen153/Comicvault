import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests
from google.api_core import exceptions

# --- 1. CONFIG & API SETUP ---
st.set_page_config(page_title="ComicVault Pro", layout="wide")

gemini_key = st.secrets.get("GEMINI_API_KEY")
cv_key = st.secrets.get("COMICVINE_API_KEY")

if gemini_key:
    genai.configure(api_key=gemini_key)
    # Using 1.5-flash as it is often more stable for free-tier quotas
    model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. COMIC VINE FALLBACK FUNCTION ---
def search_comic_vine(title, issue):
    if not cv_key:
        return "Comic Vine Key missing in Secrets."
    
    # Comic Vine API Search URL
    url = f"https://comicvine.gamespot.com{cv_key}&format=json&filter=name:{title},issue_number:{issue}"
    headers = {'User-Agent': 'ComicVaultPro/1.0'}
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        if data['results']:
            first_match = data['results'][0]
            return f"Found: {first_match['volume']['name']} #{first_match['issue_number']} - {first_match.get('name', 'No Title')}"
        return "No exact match found on Comic Vine."
    except Exception as e:
        return f"Database error: {e}"

# --- 3. THE INTERFACE ---
st.title("📚 ComicVault Pro")
st.sidebar.title("Menu")
page = st.sidebar.radio("Go to", ["Scan & Add", "My Collection"])

if page == "Scan & Add":
    st.header("Scan a Comic")
    picture = st.camera_input("Take a photo of the cover")

    if picture:
        img = Image.open(picture)
        st.image(img, width=300)

        if st.button("Identify with AI"):
            with st.spinner("Analyzing..."):
                try:
                    prompt = "Identify this comic book. Return ONLY: Publisher, Series, Issue Number."
                    response = model.generate_content([prompt, img])
                    st.success(response.text)
                except exceptions.ResourceExhausted:
                    st.error("⚠️ Gemini is at its limit (429 Error). Please wait 60 seconds or use the Database Search below.")
                except Exception as e:
                    st.error(f"Error: {e}")

    st.divider()
    st.subheader("Database Search (Backup)")
    col1, col2 = st.columns(2)
    with col1:
        search_t = st.text_input("Title", "Green Lantern")
    with col2:
        search_i = st.text_input("Issue #", "101")
    
    if st.button("Search Database"):
        with st.spinner("Checking Comic Vine..."):
            result = search_comic_vine(search_t, search_i)
            st.info(result)

elif page == "My Collection":
    st.info("Your vault is currently empty.")
