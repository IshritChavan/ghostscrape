import os
import textwrap
import requests
from bs4 import BeautifulSoup
import streamlit as st
import openai

# ---------- CONFIG ----------
openai.api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    st.error("OPENAI_API_KEY is not set. Add it in Settings → Secrets.")
    st.stop()

MAX_WORDS = 1200            # trim very long pages
MODEL     = "gpt-3.5-turbo"

# ---------- SCRAPER ----------
def extract_text(url: str) -> str:
    """Fetch page and return concatenated <p> text."""
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        return f"Error fetching URL: {e}"

    soup = BeautifulSoup(resp.text, "html.parser")
    paragraphs = soup.find_all("p")
    text = "\n\n".join(p.get_text(" ", strip=True) for p in paragraphs)
    return text or "No readable text found on this page."

# ---------- UI ----------
st.set_page_config(page_title="GhostScrape", layout="centered")
st.title("👻 GhostScrape")
st.caption("Scrape any public URL and rewrite it instantly with AI.")

url = st.text_input("Paste a URL (blog, news, product page, etc.)")

if st.button("Rewrite It!") and url:
    with st.spinner("Scraping page…"):
        original = extract_text(url)
        if original.startswith("Error") or original == "No readable text found on this page.":
            st.error(original)
            st.stop()

        trimmed = " ".join(original.split()[:MAX_WORDS])   # limit token cost

    prompt = textwrap.dedent(f"""
        Rewrite the following content so it is unique, human-like, and SEO-friendly.
        Keep the same facts but change the wording naturally.
        ---
        {trimmed}
    """)

    with st.spinner("Rewriting with GPT…"):
        try:
            res = openai.ChatCompletion.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000,
            )
            rewritten = res.choices[0].message.content.strip()
        except Exception as e:
            st.error(f"OpenAI error: {e}")
            st.stop()

    st.subheader("✅ Rewritten Content")
    st.code(rewritten, language="markdown")
    st.download_button("Download .txt", data=rewritten, file_name="ghostscrape.txt")

st.markdown("---")
st.caption("Need longer rewrites or batch mode? Email **ghostscrape@pm.me**")
