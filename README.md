# Hunting Copilot

A tool for scanning potential security threats and phishing attempts targeting specific brands using Google dork queries.

## Features
- Advanced Google dork query generation using LLMs
- Multiple search categories (phishing, domain impersonation, etc.)
- Configurable LLM models and parameters
- Real-time search execution
- Results export in Excel and TXT formats
- Live statistics and status updates

## Setup


1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

1. Install requirements:
```bash
pip install -r requirements.txt
```

1. Get required API keys:
   - GROQ API key: Sign up at https://console.groq.com
   - Serper API key: Sign up at https://serper.dev

2. Set up environment variables:
   Create a `.env` file in the project root:
```bash
GROQ_API_KEY=your_groq_api_key_here
SERPER_API_KEY=your_serper_api_key_here
```

## Running the App

1. Start the application:
```bash
python app.py (Backend)

streamlit run your_script.py (UI)

```

2. User Input:
   - Enter a brand name to scan
   - Configure API keys if not set in environment
   - Select LLM model and parameters
   - Click "Start Scan"
   - View results and extract it in seprate file

## Configuration Options

- **Models**: Choose from various Groq models:
  - llama3-70b-8192 (default)
  - mixtral-8x7b-32768
  - llama-3.1-8b-instant (faster)
  - And more...

- **Advanced Settings**:
  - Temperature: Controls query generation creativity (0.0-1.0)
  - Query Timeout: Maximum wait time per search (10-60 seconds)



## Notes

- Rate limits apply for both Groq and Serper APIs
- Large scans may take significant time to complete
- Some queries may timeout or fail - these are logged separately
- Results are saved automatically after each scan

