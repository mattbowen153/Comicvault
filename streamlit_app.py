import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests
from google.api_core import exceptions

# --- 1. CONFIG & API SETUP ---
st.set_page_config(page_title="ComicVault Pro", layout="wide")

# Get keys from Streamlit Secrets
gemini_key = st.secrets.get("GEMINI_API_KEY")
cv_key = st.secrets.get("COMICVINE_API_KEY")

if gemini_key:
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.warning("⚠️ GEMINI_API_KEY not found in Streamlit Secrets.")

# --- 2. COMIC VINE SEARCH FUNCTION ---
def search_comic_vine(title, issue):
    if not cv_key:
        return "Comic Vine Key missing in Secrets."
    
    clean_title = title.replace(" ", "%20")
    # Using the standard Comic Vine issues filter
    url = f"https://comicvine.gamespot.com{cv_key}&format=json&filter=name:{clean_title},issue_number:{issue}"
    headers = {'User-Agent': 'ComicVaultPro/1.0'}
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        if data.get('results'):
            # Grabbing the first match from the list
            res = data['results'][0] if isinstance(data['results'], list) else data['results']
            vol_name = res.get('volume', {}).get('name', 'Unknown Series')
            iss_num = res.get('issue_number', '??')
            return f"✅ Database Match: {vol_name} #{iss_num}"
        return "❌ No exact match found on Comic Vine."
    except Exception as e:
        return f"⚠️ Database error: {e}"

# --- 3. SIDEBAR NAVIGATION ---
st.sidebar.title("Menu")
page = st.sidebar.radio("Go to", ["Scan & Add", "My Collection"])

# --- 4. SCAN & ADD PAGE ---
if page == "Scan & Add":
    st.title("📚 ComicVault Pro")
    st.header("Scan a Comic Cover")
    
    picture = st.camera_input("Capture comic cover")

    if picture:
        img = Image.open(picture)
        st.image(img, width=300, caption="Scan Preview")

        if st.button("Identify with AI"):
            if not gemini_key:
                st.error("Missing Gemini API Key.")
            else:
                with st.spinner("Analyzing with AI..."):
                    try:
                        # Improved prompt for DC, Image, Dark Horse, etc.
                        prompt = "Identify this comic book. Return ONLY: Publisher, Series, Issue Number."
                        response = model.generate_content([prompt, img])
                        st.success(f"AI Result: {response.text}")
                    except exceptions.ResourceExhausted:
                        st.error("⚠️ AI Limit reached (429). Please wait 60s or use the Database Search below.")
                    except Exception as e:
                        st.error(f"AI Error: {e}")

    st.divider()
    st.subheader("Manual / Database Search")
    st.write("Use this if the AI is busy or identifies the wrong book.")
    
    col1, col2 = st.columns(2)
    with col1:
        search_t = st.text_input("Series Title", "Green Lantern")
    with col2:
        search_i = st.text_input("Issue #", "101")
    
    if st.button("Search Comic Vine"):
        with st.spinner("Querying Database..."):
            result = search_comic_vine(search_t, search_i)
            st.info(result)

# --- 5. MY COLLECTION PAGE ---
elif page == "My Collection":
    st.header("Your Vault")
    st.info("Your saved comics will appear here in the next update!")

st.markdown("---")
st.write("Deployed on Streamlit Cloud")
