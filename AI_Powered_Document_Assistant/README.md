# AI-Powered Document Assistant

A Streamlit prototype that accepts PDF or TXT files, retrieves relevant text, and displays supporting excerpts.

## Modes
- **Free demo (no API call):** Local keyword retrieval and extractive sentence selection. No OpenAI API call is made.
- **OpenAI API:** Optional answer generation using the OpenAI API. API billing may apply.

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Install dependencies: `pip install -r requirements.txt`
4. Start the app: `streamlit run app.py`
5. Open the local URL printed in the terminal (usually http://localhost:8501).

## Test
Upload `sample_document.txt`, keep **Free demo (no API call)** selected, and ask:
- `What are the support hours?`
- `What is the escalation process?`

The free mode is not an LLM and may not understand every phrasing. Verify important information against the source document.

## Privacy
Do not upload confidential, personal, medical, or sensitive files. Do not commit API keys to source control.
