import streamlit as st
from collections import Counter
import re

st.set_page_config(page_title="SEP Scanner + Tech Term Extractor & Summary", layout="wide")
st.title("Patent Text Analyzer: SEP Scanner + Key Terms + Summary")
st.markdown("""
Paste patent text (abstract + claims work best)  
→ Get SEP/telecom flags  
→ Extract key technology terms  
→ Short summary of meaning
""")

# ── Keyword lists ──
telecom_keywords = [
    "5G", "NR", "New Radio", "LTE", "4G", "MIMO", "Massive MIMO", "Beamforming",
    "base station", "gNB", "eNB", "user equipment", "UE", "RAN", "core network",
    "3GPP", "ETSI", "standard", "specification", "TS 38", "Release 15", "Release 16",
    "OFDM", "Polar code", "LDPC", "network slice", "edge computing", "IoT", "URLLC"
]

sep_indicators = [
    "standard-essential", "SEP", "essential patent", "declared essential",
    "FRAND", "3GPP standard", "ETSI declaration", "standards body", "essentiality"
]

# ── Input ──
text_input = st.text_area("Paste patent text (abstract, claims, description...)", height=350)

if text_input:
    text = text_input.strip()
    text_lower = text.lower()

    # ── 1. Telecom / SEP detection ──
    telecom_hits = sum(text_lower.count(k.lower()) for k in telecom_keywords)
    sep_hits = sum(text_lower.count(k.lower()) for k in sep_indicators)

    if sep_hits > 0 or telecom_hits > 8:
        potential = "High"
        color = "error"
    elif telecom_hits > 3:
        potential = "Medium"
        color = "warning"
    else:
        potential = "Low"
        color = "success"

    found_telecom = [k for k in telecom_keywords if k.lower() in text_lower]
    found_sep = [k for k in sep_indicators if k.lower() in text_lower]

    st.markdown(f"### SEP / Telecom Potential: **:{color}[{potential}]**")
    st.markdown(f"- Telecom keywords: **{telecom_hits}** ({', '.join(found_telecom) if found_telecom else 'none'})")
    st.markdown(f"- SEP indicators: **{sep_hits}** ({', '.join(found_sep) if found_sep else 'none'})")

    # ── 2. Key technology terms extraction (simple frequency + filtering) ──
    st.subheader("Detected Key Technology Terms")

    # Clean and tokenize roughly
    words = re.findall(r'\b[a-zA-Z0-9\-/]+\b', text_lower)
    stop_words = {'the', 'and', 'or', 'in', 'on', 'at', 'to', 'of', 'for', 'with', 'by', 'as', 'is', 'are', 'a', 'an', 'this', 'that', 'said', 'method', 'device', 'system', 'according', 'claim', 'wherein'}

    filtered_words = [w for w in words if w not in stop_words and len(w) > 3]

    # Count bigrams (two-word phrases) and single words
    bigrams = [' '.join(filtered_words[i:i+2]) for i in range(len(filtered_words)-1)]
    all_terms = filtered_words + bigrams

    term_counts = Counter(all_terms)
    top_terms = term_counts.most_common(12)

    if top_terms:
        terms_str = ", ".join([f"**{term}** ({count})" for term, count in top_terms])
        st.markdown(terms_str)
    else:
        st.info("No meaningful terms detected (text too short or generic).")

    # ── 3. Simple extractive summary ──
    st.subheader("Short Summary of the Patent Text")

    # Split into sentences
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text.strip())

    # Score sentences: longer + contains keywords = better
    scored_sentences = []
    for sent in sentences:
        sent_lower = sent.lower()
        length_score = len(sent.split()) / 20.0  # normalize
        keyword_score = sum(1 for k in telecom_keywords + sep_indicators if k.lower() in sent_lower)
        total_score = length_score + keyword_score * 1.5
        scored_sentences.append((total_score, sent.strip()))

    # Take top 2-3 sentences
    scored_sentences.sort(reverse=True)
    summary_sentences = [sent for score, sent in scored_sentences[:3] if len(sent) > 40]

    if summary_sentences:
        summary = " ".join(summary_sentences)
        st.markdown(summary)
        st.caption("Extractive summary: most representative sentences (keyword-weighted + length)")
    else:
        st.info("Text too short or no clear sentences detected.")

    # ── Final analyst draft report ──
    st.subheader("Analyst Draft Notes")
    notes = f"""
Patent Quick Scan Report

• Potential: {potential} SEP/Telecom relevance
• Telecom keywords: {telecom_hits} ({', '.join(found_telecom) if found_telecom else 'none'})
• SEP indicators: {sep_hits} ({', '.join(found_sep) if found_sep else 'none'})
• Key technology terms: {', '.join([t[0] for t in top_terms[:8]]) or 'none prominent'}

Summary of invention (extracted):
{summary or 'No sufficient content to summarize.'}

Recommended actions:
- {'High priority SEP check – look for ETSI declaration' if potential == 'High' else 'Likely implementation patent'}
- Search family & forward citations on Google Patents / Espacenet
- Compare with 3GPP specs if telecom keywords present
"""

    st.code(notes, language="markdown")

    st.download_button(
        "Download Notes (.txt)",
        notes,
        file_name="patent_scan_notes.txt",
        mime="text/plain"
    )

else:
    st.info("Paste text from a patent (abstract + claims recommended) to analyze.")