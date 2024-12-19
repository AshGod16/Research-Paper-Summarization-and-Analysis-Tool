from transformers import pipeline
from tqdm import tqdm
import re

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def chunk_text(text, max_chunk_size):
    """Chunks text intelligently by trying to split on sentence boundaries"""
    # Split text into sentences rather than arbitrary character cuts
    sentences = re.split('(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        sentence_length = len(sentence)
        if current_length + sentence_length <= max_chunk_size:
            current_chunk.append(sentence)
            current_length += sentence_length
        else:
            # Save current chunk
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            # Start new chunk
            current_chunk = [sentence]
            current_length = sentence_length
            
    # Add the last chunk if it exists
    if current_chunk:
        chunks.append(' '.join(current_chunk))
        
    return chunks

def extract_key_sections(text):
    """Extract important sections like abstract, methods, results"""
    sections = {
        'abstract': '',
        'introduction': '',
        'methods': '',
        'results': '',
        'conclusion': ''
    }
    
    # Use regex patterns to identify sections
    section_patterns = {
        'abstract': r'Abstract\s*(.*?)(?=\d{1,2}\s+Introduction|\n\n)',
        'introduction': r'Introduction\s*(.*?)(?=\d{1,2}\s+|Method|Methodology)',
        'methods': r'(?:\d{1,2}\s+)?Method(?:ology|s)?\s*(.*?)(?=\d{1,2}\s+|Results|Experiments)',
        'results': r'(?:\d{1,2}\s+)?(?:Results|Experiments)\s*(.*?)(?=\d{1,2}\s+|Conclusion|Discussion)',
        'conclusion': r'(?:\d{1,2}\s+)?Conclusion\s*(.*?)(?=References|Bibliography|\Z)'
    }
    
    for section, pattern in section_patterns.items():
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            sections[section] = match.group(1).strip()
            
    return sections

def post_process_summary(summary):
    """Clean up and improve the summary output"""
    # Remove redundant information
    summary = re.sub(r'(?i)the paper|this paper|we|our', '', summary)
    
    # Clean up whitespace
    summary = re.sub(r'\s+', ' ', summary).strip()
    
    # Add bullet points to lists
    summary = re.sub(r'(?m)^(\d+\.\s)', '• ', summary)
    
    return summary

def summarize_text(text):
    sections = extract_key_sections(text)
    
    # Process each section with appropriate parameters
    section_summaries = {}
    for section_name, section_text in sections.items():
        if not section_text:
            continue
            
        # Chunk the section text
        chunks = chunk_text(section_text, max_chunk_size=500)
        
        # Summarize chunks with section-specific parameters
        chunk_summaries = []
        for chunk in tqdm(chunks, desc=f"Summarizing {section_name}"):
            summary = summarizer(
                "summarize: " + chunk,
                max_length=80,
                min_length=30,
                do_sample=False,
                temperature=0.7
            )[0]['summary_text']
            chunk_summaries.append(summary)
            
        section_summaries[section_name] = " ".join(chunk_summaries)
    
    # Combine summaries with appropriate formatting
    final_summary = []
    if sections['abstract']:
        final_summary.append("Abstract: " + section_summaries['abstract'])
    if sections['introduction']:
        final_summary.append("\nKey Points:\n" + section_summaries['introduction'])
    if sections['methods']:
        final_summary.append("\nMethodology:\n" + section_summaries['methods'])
    if sections['results']:
        final_summary.append("\nResults:\n" + section_summaries['results'])
    if sections['conclusion']:
        final_summary.append("\nConclusion:\n" + section_summaries['conclusion'])
        
    return post_process_summary("\n".join(final_summary))