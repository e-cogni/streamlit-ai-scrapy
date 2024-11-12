from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import streamlit as st
import requests
from bs4 import BeautifulSoup
import extruct
from w3lib.html import get_base_url

# Configurações do Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")  # Executar em modo headless
chrome_options.add_argument("--lang=pt-BR")  # idioma do navegador
chrome_options.timeouts = { 'script': 5000 }

# Lista de domínios conhecidos e seus seletores de conteúdo principal
known_domains = {
    "www.bbc.com": "main",
    "cnn.com": "div.l-container",
    "www.cnnbrasil.com.br": "div.single-content",
    # Adicione mais domínios e seletores conforme necessário
}

def get_driver(url):
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(0.5)
    driver.get(url)
    return driver

def extract_content(driver, url):
    domain = url.split("/")[2]
    print(domain)
    selector = known_domains.get(domain, "body")

    try:
        main_content = driver.find_element(By.CSS_SELECTOR, selector)
        paragraphs = main_content.find_elements(By.TAG_NAME, "p")
        print(p.text for p in paragraphs)
        content = "\n".join([p.text for p in paragraphs])
    except TimeoutException:
        content = "Conteúdo principal não encontrado."

    return content

# Função para extrair meta dados
def extract_metadata(driver):
    metadata = {
        "title": driver.title,
        "description": driver.find_element(By.NAME, "description").get_attribute("content") if driver.find_elements(By.NAME, "description") else "N/A",
        "og_title": driver.find_element(By.CSS_SELECTOR, 'meta[property="og:title"]').get_attribute("content") if driver.find_elements(By.CSS_SELECTOR, 'meta[property="og:title"]') else "N/A",
        "og_description": driver.find_element(By.CSS_SELECTOR, 'meta[property="og:description"]').get_attribute("content") if driver.find_elements(By.CSS_SELECTOR, 'meta[property="og:description"]') else "N/A",
        "og_image": driver.find_element(By.CSS_SELECTOR, 'meta[property="og:image"]').get_attribute("content") if driver.find_elements(By.CSS_SELECTOR, 'meta[property="og:image"]') else "N/A",
    }

    return metadata

# Função para extrair dados estruturados
def extract_structured_data(driver):
    base_url = driver.current_url
    data = extruct.extract(driver.page_source, base_url=base_url)
    return data


# Função principal do Streamlit
def main():
    st.title("News Summarizer - Selenium")

    url = st.text_input("Enter the URL of the news article:")

    if url is not None and st.button("Summarize"):
        with st.spinner("Carregando..."):
            driver = get_driver(url)
            content = extract_content(driver, url)
            metadata = extract_metadata(driver)
            structured_data = extract_structured_data(driver)
            #driver.quit()

            st.subheader("Metadata")
            st.json(metadata)

            st.subheader("Structured Data")
            st.json(structured_data)
            driver.quit()

    if content:
        st.subheader("Content")
        content = st.text_area("Conteudo", content)

if __name__ == "__main__":
    main()