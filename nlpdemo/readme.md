# Installation and Running

```bash
# 1. Go to the nlpdemo directory
cd nlpdemo

# 2. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# 3. Install requirements
pip install -r requirements.txt

# 4. Set up environment variables in .env file:
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key

# 5. Run the app
python app.py
```

The app will launch in your web browser after running.
