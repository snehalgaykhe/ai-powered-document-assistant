import re
import streamlit as st
from pypdf import PdfReader

st.set_page_config(page_title="AI Document Assistant", page_icon="📄", layout="wide")
st.title("📄 AI-Powered Document Assistant")
st.caption("Ask questions about a document and review the passages that support the result.")

with st.sidebar:
    st.header("Settings")
    mode = st.radio(
        "Answer mode",
        ["Free demo (no API call)", "OpenAI API (may incur cost)"],
        index=0,
        help="Free demo extracts relevant sentences locally. OpenAI mode sends selected excerpts to the API."
    )
    api_key = ""
    model = "gpt-4o-mini"
    if mode == "OpenAI API (may incur cost)":
        api_key = st.text_input("OpenAI API key", type="password", help="Never share or commit your API key.")
        model = st.selectbox("Answer model", ["gpt-4o-mini", "gpt-4.1-mini"], index=0)
    else:
        st.info("Free demo mode runs locally and does not call a paid API. Answers are extractive, not LLM-generated.")
    st.info("Avoid uploading confidential, personal, medical, or sensitive files.")

uploaded = st.file_uploader("Upload a PDF or TXT document", type=["pdf", "txt"])


def extract_text(file):
    """Extract text from a TXT or text-based PDF upload."""
    if file.name.lower().endswith(".pdf"):
        reader = PdfReader(file)
        pages = []
        for page_number, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ""
            if page_text.strip():
                pages.append(f"[Page {page_number}]\n{page_text}")
        return "\n\n".join(pages)
    return file.getvalue().decode("utf-8", errors="replace")


def chunk_text(text, max_chars=1400, overlap=180):
    """Split text into overlapping chunks without discarding long paragraphs."""
    text = re.sub(r"[ \t]+", " ", text)
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks = []
    current = ""
    for paragraph in paragraphs:
        remaining = paragraph
        while len(remaining) > max_chars:
            piece = remaining[:max_chars]
            if current:
                chunks.append(current)
                current = ""
            chunks.append(piece)
            remaining = remaining[max_chars - overlap:]
        candidate = f"{current}\n\n{remaining}".strip() if current else remaining
        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                chunks.append(current)
            current = remaining
    if current:
        chunks.append(current)
    return chunks


STOP_WORDS = {
    "the", "a", "an", "and", "or", "is", "are", "was", "were", "to", "of",
    "in", "on", "for", "with", "what", "which", "who", "when", "where",
    "how", "does", "do", "can", "could", "about", "from", "this", "that",
    "it", "be", "as", "by", "at", "if", "i", "you", "your", "me", "my",
    "please", "tell", "explain", "process"
}


def terms_in(text):
    """Return lowercase searchable terms, excluding common question words."""
    return set(re.findall(r"\b[a-zA-Z0-9]{2,}\b", text.lower())) - STOP_WORDS


def lexical_retrieve(question, chunks, top_k=4):
    """Rank chunks by keyword overlap."""
    question_terms = terms_in(question)
    if not question_terms:
        return []
    scored = []
    for index, chunk in enumerate(chunks):
        chunk_terms = terms_in(chunk)
        overlap = len(question_terms & chunk_terms)
        score = overlap / max(len(question_terms), 1)
        if score > 0:
            scored.append((score, index, chunk))
    scored.sort(key=lambda item: (item[0], -len(item[2])), reverse=True)
    return [(index, chunk, score) for score, index, chunk in scored[:top_k]]


def is_heading(sentence):
    stripped = sentence.strip()
    return stripped.endswith(":") or (
        len(stripped.split()) <= 5
        and not stripped.endswith((".", "!", "?"))
    )


def local_extractive_answer(question, matches):
    """Return source sentences; include explanatory sentences under a matching heading."""
    question_terms = terms_in(question)
    candidates = []
    seen = set()

    for chunk_index, chunk, chunk_score in matches:
        sentences = [
            part.strip(" \t-*•")
            for part in re.split(r"(?<=[.!?])\s+|\n+", chunk)
            if part.strip(" \t-*•")
        ]

        for sentence_index, sentence in enumerate(sentences):
            if len(sentence) < 12:
                continue

            sentence_terms = terms_in(sentence)
            overlap = len(question_terms & sentence_terms)
            heading_match = is_heading(sentence) and bool(
                question_terms & terms_in(sentence.rstrip(":"))
            )

            if heading_match:
                for following in sentences[sentence_index + 1:sentence_index + 4]:
                    if is_heading(following):
                        break
                    if len(following) < 12:
                        continue
                    key = following.lower()
                    if key not in seen:
                        seen.add(key)
                        candidates.append((2.0 + chunk_score, chunk_index, following))
            elif overlap > 0 and not is_heading(sentence):
                score = overlap / max(len(question_terms), 1) + chunk_score * 0.1
                key = sentence.lower()
                if key not in seen:
                    seen.add(key)
                    candidates.append((score, chunk_index, sentence))

    candidates.sort(key=lambda item: item[0], reverse=True)
    return [(chunk_index, sentence) for _, chunk_index, sentence in candidates[:4]]


if uploaded:
    try:
        document_text = extract_text(uploaded)
    except Exception as exc:
        st.error(f"Could not read this file: {exc}")
        st.stop()

    if not document_text.strip():
        st.error("No readable text was found. If this is a scanned PDF, run OCR first or upload a text-based PDF.")
        st.stop()

    chunks = chunk_text(document_text)
    st.success(f"Loaded **{uploaded.name}** · {len(document_text):,} characters · {len(chunks)} text chunks")
    with st.expander("Preview extracted text"):
        preview = document_text[:5000]
        if len(document_text) > 5000:
            preview += "\n\n[Preview shortened]"
        st.text(preview)

    question = st.text_area("Ask a question about this document", placeholder="Example: What are the support hours?", height=90)
    ask = st.button("Find answer", type="primary", disabled=not question.strip())

    if ask:
        matches = lexical_retrieve(question, chunks)
        if not matches:
            st.warning("I couldn't find a clear text match. Try using words that appear in the document.")
        elif mode == "Free demo (no API call)":
            answer_sentences = local_extractive_answer(question, matches)
            if not answer_sentences:
                st.warning("I couldn't find a sentence that clearly answers this question in the uploaded document.")
            else:
                st.subheader("Answer (free demo — extracted from the document)")
                for chunk_index, sentence in answer_sentences:
                    st.write(f"• {sentence}")
                st.caption("This mode selects existing sentences; it does not use an LLM or invent a paraphrased answer.")
                with st.expander("View retrieved excerpts"):
                    for chunk_index, chunk, score in matches:
                        st.markdown(f"**Excerpt {chunk_index + 1}** · relevance score {score:.2f}")
                        st.write(chunk)
        else:
            if not api_key:
                st.warning("Enter your OpenAI API key in the sidebar, or switch to Free demo mode.")
            else:
                try:
                    from openai import OpenAI
                    context = "\n\n".join(
                        f"[Excerpt {chunk_index + 1}]\n{chunk}"
                        for chunk_index, chunk, _ in matches
                    )
                    system_prompt = (
                        "You are a careful document question-answering assistant. Answer using only the supplied excerpts. "
                        "If the excerpts do not contain the answer, say: 'I couldn't find that information in the uploaded document.' "
                        "Do not invent facts. Keep the answer clear and concise. Cite excerpt numbers when possible."
                    )
                    client = OpenAI(api_key=api_key)
                    with st.spinner("Reading relevant passages and drafting an answer..."):
                        response = client.chat.completions.create(
                            model=model,
                            temperature=0.1,
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": f"QUESTION:\n{question}\n\nDOCUMENT EXCERPTS:\n{context}"},
                            ],
                        )
                    st.subheader("Answer (OpenAI API)")
                    st.write(response.choices[0].message.content or "No answer was returned.")
                    with st.expander("View retrieved excerpts"):
                        for chunk_index, chunk, score in matches:
                            st.markdown(f"**Excerpt {chunk_index + 1}** · relevance score {score:.2f}")
                            st.write(chunk)
                except Exception as exc:
                    st.error(f"Could not generate an answer. Check API credits, key, model access, and internet connection. Details: {exc}")
else:
    st.markdown("""
    **How to use**
    1. Choose **Free demo (no API call)** in the sidebar to test without API credits.
    2. Upload a text-based PDF or TXT file.
    3. Ask a question using words that appear in the document.
    4. Review the extracted answer sentences and supporting excerpts.

    The free demo uses local keyword matching and sentence extraction. It is not a generative AI answer; switch to OpenAI API mode only if API billing is configured.
    """)

st.divider()
st.caption("Prototype for demonstration. Verify important answers against the original document.")
