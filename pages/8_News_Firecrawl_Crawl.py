import streamlit as st
from firecrawl import FirecrawlApp

# Configurações do Firecrawl
firecrawl_key = st.secrets["FIRECRAWL_API_KEY"]
firecrawl = FirecrawlApp(api_key=firecrawl_key)

# Lista de domínios conhecidos e seus seletores de conteúdo principal
known_domains = {
    "www.bbc.com": "main",
    "cnn.com": "div.l-container",
    "www.cnnbrasil.com.br": "div.single-content",
    "fdr.com.br": "article.singular__content"
    # Adicione mais domínios e seletores conforme necessário
}

# Função para extrair conteúdo usando Firecrawl
def extract_content(url):
    domain = url.split("/")[2]
    selector = known_domains.get(domain, "body")
    params = {'formats': ['rawHtml', 'html'], 'includeTags': [selector, 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'ul', 'ol', 'li', 'blockquote', 'table', 'tr', 'td', 'th']}

    try:
        result = firecrawl.scrape_url(url, params)
        content = result['html']
        content_raw = result['rawHtml']
        metadata = result['metadata']
    
    except Exception as e:
        content = f"Erro ao extrair conteúdo: {e}"
        content_raw = ""

    return content, content_raw, metadata

# Função principal do Streamlit
def main():
    st.title("News Indexing with Firecrawl")

    with st.form("indexer"):
        url = st.text_input("Enter the URL of the news article:", key="url")
        submitted = st.form_submit_button("Index News")

        if submitted:
            if not url:
                st.error("Please enter a URL.")
            else:
                with st.spinner("Loading..."):
                    content, content_raw,  metadata = extract_content(url)
                    st.header("Result")
                    st.subheader("Content")
                    st.text_area("Content", content, key="content")
                    st.subheader("Raw Content")
                    st.text_area("Raw Content", content_raw, key="content_raw")
                    st.subheader("Metadata")
                    st.json(metadata)

if __name__ == "__main__":
    main()
