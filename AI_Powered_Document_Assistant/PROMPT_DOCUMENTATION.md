# Prompt Documentation

## Project goal
Build a small document assistant that answers questions using uploaded document text and exposes supporting passages.

## Prompt used for the optional OpenAI API mode
System prompt:
> You are a careful document question-answering assistant. Answer using only the supplied excerpts. If the excerpts do not contain the answer, say: 'I couldn't find that information in the uploaded document.' Do not invent facts. Keep the answer clear and concise. Cite excerpt numbers when possible.

User prompt template:
> QUESTION: {question}
>
> DOCUMENT EXCERPTS: {retrieved excerpts}

## Local free-demo approach
The free demo does not use an LLM prompt. It splits document text into chunks, ranks chunks using keyword overlap, extracts relevant sentences, and displays excerpts for verification. When a matching section heading is found, it attempts to include following explanatory sentences.

## Testing and revisions
Record actual results before submitting. Do not claim the optional OpenAI mode worked unless it was tested with a working API account.
