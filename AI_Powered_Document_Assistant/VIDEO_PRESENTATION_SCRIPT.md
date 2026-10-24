# 2–3 Minute Project Demo Script

## 0:00–0:20 — Introduction
“Hello, this is my AI-Powered Document Assistant, a technology automation prototype. It lets a user upload a PDF or text file, ask a question, and inspect the source passages used to answer.”

## 0:20–0:45 — Tools
“I built the interface with Python and Streamlit. I use pypdf to extract text from PDFs and regular expressions plus keyword matching to split and retrieve document content. An optional OpenAI API mode is included, but this demo uses the free local mode.”

## 0:45–1:30 — Live demo
“Here I upload sample_document.txt. I ask, ‘What is the escalation process?’ The app retrieves relevant text from the document and displays the source excerpt. I can expand the excerpt section to verify the result against the original content.”

## 1:30–2:00 — Approach and limitations
“The local mode does not call a paid API. It uses keyword retrieval and extractive sentence selection, so it is not a generative LLM answer and may miss some questions if the wording differs from the source. The optional API mode requires a configured API account with available billing credits.”

## 2:00–2:30 — Outcome and next steps
“The prototype demonstrates document text extraction, basic retrieval, and source transparency. Possible next improvements include stronger semantic search, OCR for scanned PDFs, and more thorough tests across different document layouts.”

Before recording, run the actual questions and describe only results you personally observe.
