import streamlit as st

st.set_page_config(page_title="ComicVault Pro", layout="wide")

st.title("ComicVault Pro")
st.markdown("Welcome to your comic collection manager!")

st.sidebar.title("Menu")
page = st.sidebar.radio("Go to", ["Scan & Add", "My Collection"])

if page == "Scan & Add":
    st.header("Scan or Add Comic")
    picture = st.camera_input("Take photo of comic cover")
    if picture:
        st.image(picture, caption="Captured photo", use_column_width=True)
        title = st.text_input("Title", "Unknown")
        issue = st.text_input("Issue #", "1")
        grade = st.selectbox("Grade", ["NM", "VF", "FN", "VG", "Good", "Fair", "Poor"])
        if st.button("Analyze"):
            st.success("Analysis placeholder — add Claude/Gemini here later")

if page == "My Collection":
    st.header("My Collection")
    st.info("Collection coming soon...")

st.markdown("---")
st.write("Deployed on Streamlit Cloud — edit app.py to add features!")
