
# 🎬 GenAI Movie Recommender

A responsive movie recommendation web app built with **Streamlit**, powered by **Gemini LLM (via LangChain)** and **TMDb API**. It suggests real, recent movies based on user preferences and displays trailers, OTT links, ratings, and more.

## 🧠 Features
- Unlimited movie recommendations using Google Gemini
- Language-based filtering
- Newest releases prioritized
- Embedded trailers from YouTube
- Watch on OTT (via JustWatch)
- Dark mode UI with custom fonts and hover effects

## 🛠️ Tech Stack
- Python, Streamlit
- Google Gemini via LangChain
- TMDb API
- JustWatch (OTT search)
- HTML/CSS Styling

## 🔐 Environment Setup
1. Clone this repo
```bash
git clone https://github.com/your-username/movie-recommender.git
cd movie-recommender
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Create a `.env` file:
```env
TMDB_API_KEY=your_tmdb_api_key
GOOGLE_API_KEY=your_google_gemini_api_key
```

4. Run the app:
```bash
streamlit run app.py
```

## 📄 License
[MIT](LICENSE)

## 🙋‍♂️ Author
Vaibhav Mehta
