import streamlit as st
import requests
import os
import re
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

# Load API keys from .env
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.7
)

# Prompt template
prompt = PromptTemplate(
    input_variables=["user_input"],
    template="""
You are a helpful AI assistant. Based on the following user request, list as many real, popular or recent movies that match the description. Make sure these are actual movie titles that exist in TMDb. Do not invent fictional names. Return only the movie names in plain text, separated by line breaks. Avoid numeric sequels (e.g., use 'Part Two' instead of '2').

User Request: {user_input}

Movie List:
"""
)
chain = prompt | llm

# TMDb search function
def discover_movies_tmdb(title, lang_code):
    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": title,
        "language": "en-US",
        "include_adult": False,
        "region": "IN",
        "page": 1
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        results = response.json().get("results", [])
        if lang_code:
            results = [r for r in results if r.get("original_language") == lang_code]
        results = sorted(results, key=lambda x: x.get("release_date", ""), reverse=True)
        return results
    except:
        return []

# TMDb trailer function
def get_trailer_url(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        results = response.json().get("results", [])
        for video in results:
            if video["site"] == "YouTube" and video["type"] == "Trailer":
                return f"https://www.youtube.com/watch?v={video['key']}"
    except:
        return None

# OTT search link
def get_ott_link(title):
    return f"https://www.justwatch.com/in/search?q={title.replace(' ', '%20')}"

# Streamlit config
st.set_page_config(page_title="🎬 GenAI Movie Recommender", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    html, body, .stApp {
        background-color: #141414 !important;
        color: white !important;
        font-family: 'Poppins', sans-serif;
    }

    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

    .movie-card {
        background-color: #1f1f1f;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 0 15px rgba(255, 255, 255, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .movie-card:hover {
        transform: scale(1.02);
        box-shadow: 0 0 20px rgba(255, 255, 255, 0.2);
    }

    .movie-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: white;
        margin-top: 0.5rem;
    }

    .rating {
        color: #f5c518;
        font-weight: bold;
    }

    img {
        border-radius: 10px;
    }

    input[type="text"], .stTextInput input {
        background-color: #2a2a2a !important;
        color: white !important;
        border: 1px solid #444 !important;
        padding: 10px;
        font-size: 1rem;
    }

    input::placeholder {
        color: #cccccc !important;
        opacity: 1 !important;
    }

    .stSelectbox div[data-baseweb="select"] {
        background-color: #2a2a2a !important;
        color: white !important;
        border: 1px solid #444 !important;
        font-size: 1rem;
    }

    .stSelectbox [data-baseweb="popover"] {
        background-color: #1e1e1e !important;
        color: white !important;
    }

    .stButton > button {
        background-color: #f63366 !important;
        color: white !important;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background-color: #ff4b6e !important;
        box-shadow: 0 0 10px rgba(255, 99, 132, 0.4);
        transform: scale(1.02);
    }

    label, .css-1aumxhk, .css-1v0mbdj {
        color: white !important;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

# UI
st.title("🍿 GenAI Movie Recommender")
st.markdown("### Get personalized movie suggestions powered by Gemini + TMDb")

user_input = st.text_input("Describe your movie preference:", placeholder="e.g., emotional Tamil drama, action-packed English thriller")

# Language map
language_display_to_code = {
    "All Languages": None,
    "Hindi": "hi",
    "English": "en",
    "Tamil": "ta",
    "Telugu": "te",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Marathi": "mr",
    "Punjabi": "pa",
    "Korean": "ko",
    "Japanese": "ja",
    "Spanish": "es",
    "French": "fr"
}
selected_lang_display = st.selectbox("Choose movie language (optional):", list(language_display_to_code.keys()))
selected_lang_code = language_display_to_code[selected_lang_display]

# Recommendations
if st.button("🍿 Get Movie Recommendations"):
    with st.spinner("🎥 Gemini is thinking..."):
        try:
            full_prompt = f"{user_input} (Language: {selected_lang_display})"
            response = chain.invoke({"user_input": full_prompt}).content.strip()
            movie_names = [movie.strip() for movie in response.split("\n") if movie.strip()]

            st.subheader("🎬 Gemini-Suggested Movies")
            match_year = re.search(r"\b(19|20)\d{2}\b", user_input)
            user_year = match_year.group() if match_year else None

            cols = st.columns(3)

            for i, movie in enumerate(movie_names):
                clean_title = re.sub(r"\(.*?\)|:.*", "", movie).strip()
                results = discover_movies_tmdb(clean_title, selected_lang_code)

                if user_year:
                    results = [res for res in results if res.get("release_date", "").startswith(user_year)]

                with cols[i % 3]:
                    if results:
                        top_result = results[0]
                        title = top_result.get("title", "Untitled")
                        rating = top_result.get("vote_average", "N/A")
                        date = top_result.get("release_date", "N/A")
                        overview = top_result.get("overview", "No description available.")
                        poster = top_result.get("poster_path")
                        poster_url = f"https://image.tmdb.org/t/p/w500{poster}" if poster else None
                        trailer_url = get_trailer_url(top_result.get("id", ""))

                        st.markdown('<div class="movie-card">', unsafe_allow_html=True)
                        if poster_url:
                            st.image(poster_url, use_container_width=True)
                        st.markdown(f"<div class='movie-title'>{title}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='rating'>⭐ {rating}</div> | 📅 {date}", unsafe_allow_html=True)
                        st.markdown(f"<div style='font-size: 0.85rem; color: #ccc;'>{overview}</div>", unsafe_allow_html=True)
                        if trailer_url:
                            st.markdown(f"[🎬 Watch Trailer]({trailer_url})", unsafe_allow_html=True)
                        else:
                            st.markdown("*🎬 Trailer not available*")
                        ott_url = get_ott_link(title)
                        st.markdown(f"[▶️ Available on OTT Platforms]({ott_url})", unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.warning(f"🚫 No TMDb results for: {movie}")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
