import os
import textwrap
import streamlit as st
import openai
from newspaper import Article

# === CONFIG ===
openai.api_key = os.getenv("OPENAI_API_KEY")
MAX_CHARS = 6000

st.set_page_config(page_title="GhostScrape", layout="centered")
st.title("👻 GhostScrape")
st.caption("Scrape any article or product page and rewrite it instantly using AI.")

url = st.text_input("Paste a URL (blog, product, etc.)")

if st.button("Rewrite It!") and url:
    with st.spinner("Scraping page..."):
        try:
            art = Article(url)
            art.download(); art.parse()
            text = art.text[:MAX_CHARS]
        except Exception as e:
            st.error(f"Scrape failed: {e}")
            st.stop()

    prompt = textwrap.dedent(f"""
        Rewrite the following content to be unique, human-like, and SEO-friendly.
        Keep core ideas but use your own language:
        ---
        {text}
    """)

    with st.spinner("Rewriting with GPT..."):
        try:
            res = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1200
            )
            rewritten = res.choices[0].message.content.strip()
        except Exception as e:
            st.error(f"AI error: {e}")
            st.stop()

    st.subheader("✅ Rewritten Content")
    st.text_area("Copy it here:", rewritten, height=400)
    st.success("Need longer rewrites or batch mode? Email us: ghostscrape@pm.me")

st.markdown("---")
st.markdown("👻 **GhostScrape** helps you spin content ethically, fast. Use it for SEO, blogs, and eCommerce.")
