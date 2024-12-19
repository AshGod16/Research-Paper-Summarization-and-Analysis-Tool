from transformers import pipeline
from tqdm import tqdm

# Initialize summarization pipeline
summarizer = pipeline("summarization", model="google-t5/t5-small")

def summarize_text(text):
    max_chunk = 500  # BART's max token input size
    text_chunks = [text[i:i+max_chunk] for i in range(0, len(text), max_chunk)]
    print('summarizing...')
    summaries = ['summarize:' + summarizer(chunk, max_length=130, min_length=30, do_sample=False)[0]['summary_text'] for chunk in tqdm(text_chunks)]
    return " ".join(summaries)
