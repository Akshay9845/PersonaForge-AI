# PersonaForge AI

PersonaForge AI is a system that analyzes Reddit users to generate detailed personality profiles using real Reddit data and AI analysis. It features a FastAPI backend (with PRAW/AsyncPRAW for Reddit scraping, Groq as the main LLM, Gemini as fallback) and a React frontend with interactive charts and PDF export.

## Features
- Input a Reddit username or profile URL
- Scrapes posts and comments
- Builds a comprehensive AI-generated user persona
- Cites posts/comments for each persona characteristic
- Outputs persona as text, JSON, and downloadable PDF
- Interactive dashboard with charts and real Reddit content

## Technologies Used
- Python 3.9+
- FastAPI (backend API)
- AsyncPRAW (Reddit scraping)
- Groq LLM (primary), Gemini LLM (fallback)
- React + Vite + Tailwind (frontend)
- ReportLab/WeasyPrint (PDF generation)

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/Akshay9845/PersonaForge-AI.git
cd PersonaForge-AI
```

### 2. Python Backend Setup
- Create a virtual environment and activate it:
```bash
python3 -m venv venv
source venv/bin/activate
```
- Install dependencies:
```bash
pip install -r requirements.txt
```
- Copy the example environment file and add your API keys:
```bash
cp env.example .env
# Edit .env and add your GROQ_API_KEY, GEMINI_API_KEY, and Reddit API credentials
```
- Start the backend server:
```bash
python3 start_server.py
```
- The API will be available at http://localhost:8080

### 3. Frontend Setup
```bash
cd personaforge-frontend
npm install
npm run dev
```
- The frontend will be available at http://localhost:5173 (or next available port)

### 4. Usage
- Open the frontend in your browser.
- Enter a Reddit username or profile URL (e.g., https://www.reddit.com/user/kojied/)
- Click "Generate" to analyze and view the persona dashboard.
- Download the PDF report if desired.

### 5. Sample Output
- Sample persona text and JSON files are saved in the `personas/` directory after analysis.

## Notes
- **API Keys:** You must provide your own Groq and Gemini API keys in the `.env` file. The repo does not include any real keys.
- **Reddit API:** Register a Reddit app to get your client ID/secret.
- **PDF Generation:** Requires `reportlab` and/or `weasyprint` (already in requirements.txt).
- **Vercel Deployment:** See `vercel.json` for environment variable mapping.

## License
MIT 