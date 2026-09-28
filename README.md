# LegalEase — AI-Powered Legal Document Generator

LegalEase is a complete Streamlit + FastAPI + Gemini application based on the supplied project specification.

## Features

- Generate legal-document drafts from:
  - Document type
  - Parties
  - Terms & conditions
  - Effective date
- FastAPI backend with `POST /generate`
- Google Gemini integration using the current `google-genai` SDK
- Editable generated document
- TXT download
- DOCX download with title, terms table, header/footer and optional logo
- PDF download with header/footer and optional logo
- HTML preview
- Health-check endpoint
- Demo/fallback mode when no Gemini key is configured
- CORS configuration
- Basic API tests
- Docker support

> Legal notice: LegalEase generates drafts for educational/productivity purposes. It is not a substitute for advice from a qualified lawyer. Users should review documents for the relevant jurisdiction before signing or relying on them.

## Project structure

```text
LegalEase/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── Dockerfile
├── Procfile
├── README.md
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── routes.py
│   └── schemas.py
├── ai_core/
│   ├── __init__.py
│   └── gemini_generator.py
├── utils/
│   ├── __init__.py
│   ├── exporters.py
│   └── text_utils.py
├── assets/
│   └── README.txt
└── tests/
    ├── __init__.py
    └── test_api.py
```

## 1. Install Python

Use Python 3.10 or newer.

Check:

```bash
python --version
```

On Windows, if `python` is unavailable:

```bash
py --version
```

## 2. Open the project in VS Code

Open the `LegalEase` folder in VS Code.

## 3. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 4. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Configure Gemini

Copy `.env.example` to `.env`.

Windows:

```cmd
copy .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

Put your Gemini API key in `.env`:

```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash
```

The model is configurable so you can change it without editing Python code.

## 6. Start FastAPI

From the project root:

```bash
uvicorn backend.main:app --reload
```

The API will normally be available at:

```text
http://127.0.0.1:8000
```

Open:

```text
http://127.0.0.1:8000/
```

and:

```text
http://127.0.0.1:8000/docs
```

## 7. Start Streamlit

Open a second terminal, activate `.venv`, then:

```bash
streamlit run app.py
```

Streamlit normally opens:

```text
http://localhost:8501
```

## 8. Test without Gemini

If `GEMINI_API_KEY` is empty, LegalEase runs in safe demo mode. This lets you test the complete frontend, API, editing and download workflow without an API call.

To use real AI generation, add a valid Gemini API key and restart FastAPI.

## 9. Test the API

```bash
python -m pytest -q
```

Manual request:

```bash
curl -X POST "http://127.0.0.1:8000/generate" ^
  -H "Content-Type: application/json" ^
  -d "{\"document_type\":\"NDA\",\"parties\":\"Alice Smith (Disclosing Party), ABC Ltd (Receiving Party)\",\"terms\":\"Confidentiality applies for 2 years; Information must be protected; Either party may terminate with 15 days notice\",\"dates\":\"September 26, 2026\"}"
```

On PowerShell, use:

```powershell
$body = @{
  document_type = "NDA"
  parties = "Alice Smith (Disclosing Party), ABC Ltd (Receiving Party)"
  terms = "Confidentiality applies for 2 years; Information must be protected; Either party may terminate with 15 days notice"
  dates = "September 26, 2026"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/generate" -ContentType "application/json" -Body $body
```

## 10. Add a logo

Place a PNG/JPG image at:

```text
assets/logo.png
```

The DOCX/PDF exporter automatically uses it when present.

## 11. Docker

Build:

```bash
docker build -t legalease .
```

Run:

```bash
docker run --env-file .env -p 8000:8000 -p 8501:8501 legalease
```

The image starts both services through `start.sh`.

## 12. Important project note

The original specification selects `gemini-1.5-pro`. Gemini model availability changes over time, so this implementation does not hard-code that retired/legacy model. Set `GEMINI_MODEL` to a currently available model in your Gemini account. The default in this project is `gemini-2.5-flash`.

The supplied specification explicitly calls for Streamlit, FastAPI, Gemini, editable preview and TXT/DOCX/PDF exports. This implementation follows that architecture while using the current Google GenAI Python SDK.
