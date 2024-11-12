import streamlit as st
import requests
from bs4 import BeautifulSoup
import extruct
from w3lib.html import get_base_url

# Lista de domínios conhecidos e seus seletores de conteúdo principal
known_domains = {
    "bbc.com": "article",
    "cnn.com": "div.l-container",
    "cnn.com.br": "div.single-content",
    # Adicione mais domínios e seletores conforme necessário
}

# Função para extrair conteúdo principal
def extract_content(url):
    domain = url.split("/")[2]
    selector = known_domains.get(domain, "body")

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Extrair conteúdo principal
    main_content = soup.select_one(selector)
    if main_content:
        return main_content.get_text(strip=True)
    else:
        return "Conteúdo principal não encontrado."

# Função para extrair meta dados
def extract_metadata(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    metadata = {
        "title": soup.title.string if soup.title else "N/A",
        "description": soup.find("meta", attrs={"name": "description"})["content"] if soup.find("meta", attrs={"name": "description"}) else "N/A",
        "og_title": soup.find("meta", property="og:title")["content"] if soup.find("meta", property="og:title") else "N/A",
        "og_description": soup.find("meta", property="og:description")["content"] if soup.find("meta", property="og:description") else "N/A",
        "og_image": soup.find("meta", property="og:image")["content"] if soup.find("meta", property="og:image") else "N/A",
    }

    return metadata

# Função para extrair dados estruturados
def extract_structured_data(url):
    response = requests.get(url)
    base_url = get_base_url(response.text, response.url)
    data = extruct.extract(response.text, base_url=base_url)
    return data

# Função principal do Streamlit
def main():
    st.title("News Summarizer")

    url = st.text_input("Enter the URL of the news article:")

    if url is not None and st.button("Summarize"):
        st.write("Fetching content...")
        content = extract_content(url)
        metadata = extract_metadata(url)
        structured_data = extract_structured_data(url)

        st.subheader("Main Content")
        st.write(content)

        st.subheader("Metadata")
        st.json(metadata)

        st.subheader("Structured Data")
        st.json(structured_data)

if __name__ == "__main__":
    main()