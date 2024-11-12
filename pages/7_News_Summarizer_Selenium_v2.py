from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import streamlit as st
from bs4 import BeautifulSoup
import extruct
from w3lib.html import get_base_url

# Configurações do Selenium
slOptions = ChromeOptions()
slOptions.add_argument("--headless")  # modo headless
slOptions.add_argument("--window-size=1920,1200")  # resolucao da janela
slOptions.add_argument("--start-maximized")  
slOptions.page_load_strategy = 'eager'
# slOptions.timeouts = { 'script': 5000, 'implicit': 1000 }
# slOptions.enable_bidi = True



# variaveis
content = None
content_raw = None
screen_shot = None

# Lista de domínios conhecidos e seus seletores de conteúdo principal
known_domains = {
    "www.bbc.com": "main",
    "cnn.com": "div.l-container",
    "www.cnnbrasil.com.br": "div.single-content",
    "fdr.com.br": "article.singular__content"
    # Adicione mais domínios e seletores conforme necessário
}

# Função para obter o driver do navegador
def get_driver(url):
    driver = webdriver.Chrome(options=slOptions)
    driver.get(url)
    return driver

def extract_content(driver, url):
    domain = url.split("/")[2]
    print(domain)
    selector = known_domains.get(domain, "body")

    try:
        main_content = driver.find_element(By.CSS_SELECTOR, selector)
        paragraphs = main_content.find_elements(By.TAG_NAME, "p")
        content = "\n".join([p.text for p in paragraphs])
        content_raw = main_content.get_attribute("outerHTML")
        print(content_raw)
    
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

@st.fragment()
def content_area_editor(content):
    content = st.text_area("Content", content, key="content")
    return content

@st.fragment()
def content_title(structured_data):
    # use json-ld title if available otherwise use opengraph title
    title = structured_data.get("json-ld", [{}])[0].get("headline", None)
    return title


st.title("News Summarizer - Selenium")

with st.form("summaryzor"):
    url = st.text_input("Enter the URL of the news article:", key="url")
    
    submitted = st.form_submit_button("Summarize")


    if submitted:
        with st.spinner("Loading..."):
            driver = get_driver(url)
            content = extract_content(driver, url)
            metadata = extract_metadata(driver)
            structured_data = extract_structured_data(driver)
            screen_shot = driver.get_screenshot_as_png()
            driver.quit()
            


if content:
    st.header("Result")
    st.subheader("Content")
    content_area_editor(content)
    if metadata:
        st.subheader("Metadata Image")
        st.image(metadata["og_image"])
    if screen_shot:
        st.subheader("Screenshot")
        st.image(screen_shot)
    if structured_data:
        st.subheader("OG Data")
        st.json(structured_data["opengraph"])
    if metadata:
        st.subheader("Metadata")
        st.json(metadata)
    if structured_data:
        st.subheader("Structured Data")
        st.json(structured_data)
    print(content)








# Função principal do Streamlit
def main():

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

#if __name__ == "__main__":
#    main()