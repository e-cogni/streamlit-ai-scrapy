import streamlit as st
from firecrawl import FirecrawlApp
import extruct
import base64
from bs4 import BeautifulSoup
import requests
from lxml import etree
from io import BytesIO
from PIL import Image
import json

# Configurações do Firecrawl
firecrawl_key = st.secrets["FIRECRAWL_API_KEY"]

firecrawl = FirecrawlApp(api_key=firecrawl_key)

token = st.secrets["BROWSERLESS_API_TOKEN"]
address = st.secrets["BROWSERLESS_ADDRESS"]
headers = {
        "User-Agent": "Mozilla/5.0 (compatible; Ecognibot/2.1; +http://www.e-cogni.com/bot.html)",
        "Cache-Control": "no-cache",
        "Content-Type": "application/json"
    }

# Lista de domínios conhecidos e seus seletores de conteúdo principal
known_domains = {
    "www.bbc.com": "main",
    "cnn.com": "div.l-container",
    "www.cnnbrasil.com.br": "div.single-content",
    "fdr.com.br": "article.singular__content",
    "www.tecmundo.com.br": 'div.tec--article__body.z--px-16',
    'olhardigital.com.br':  'div.post-content.wp-embed-responsive',
    'techcrunch.com': 'div.entry-content.wp-block-post-content.is-layout-constrained.wp-block-post-content-is-layout-constrained',
    'noticias.uol.com.br': 'body > div.vl-wrapper > main > article > div:nth-child(1) > div.mt-100.container.grid > div > div',
    # auto gerado
    'www.theverge.com': 'div.c-entry-content',
    'www.wired.com': 'div.body__inner-container',
    'www.nytimes.com': 'div.StoryBodyCompanionColumn',
    'www.washingtonpost.com': 'div.article-body',
    'www.wsj.com': 'div.article-content',
    'www.bloomberg.com': 'div.body-copy-v2',
    'www.economist.com': 'div.layout-article__content',
    'www.ft.com': 'div#site-content',
    'www.businessinsider.com': 'div.article-content-container',
    'www.forbes.com': 'div.article-body-container',
    'www.inc.com': 'div.article-body',
    'www.entrepreneur.com': 'div.article-body',
    'www.fastcompany.com': 'div.article-body',
    'www.hbr.org': 'div.article.article-first-column',
    'www.nature.com': 'div.c-article-body',
    'www.sciencemag.org': 'div.article__body',
    'www.scientificamerican.com': 'div.article__body',
    'www.nationalgeographic.com': 'div.Article__Content',
    'www.newscientist.com': 'div.article__body',
    'www.sciencedaily.com': 'div#text',
    'www.livescience.com': 'div.article-content',
    'www.space.com': 'div.article-content',
    'www.nasa.gov': 'div.wysiwyg_content',
    'www.nationalgeographic.com': 'div.Article__Content',
    # Adicione mais domínios e seletores conforme necessário
}

# Função para extrair conteúdo principal usando BeautifulSoup
def extract_content(url, content_raw):
    domain = url.split("/")[2]
    selector = known_domains.get(domain, "body")

    soup = BeautifulSoup(content_raw, "html.parser")

    # Extrair conteúdo principal
    main_content = soup.select_one(selector)
    # body = soup.find("body")
    # dom = etree.HTML(str(body))
    # main_content = dom.xpath(selector)[0].text
    if main_content:
        return main_content.text
    else:
        return "Conteúdo principal não encontrado."

# Função para scrape de conteúdo usando Firecrawl
def firecrawl_scrape(url):
    domain = url.split("/")[2]
    selector = known_domains.get(domain, "body")
    params = {'formats': ['rawHtml'], 'waitFor': 2000, 'timeout': 10000}


    try:
        result = firecrawl.scrape_url(url, params)
        # content = result['html']
        content_raw = result['rawHtml']
        metadata = result['metadata']
    
    except Exception as e:
        # content = f"Erro ao extrair conteúdo: {e}"
        content_raw = ""

    return content_raw, metadata

# Funcao para scrape de conteudo usando Browserless
def browserless_scrape(url):

    request_url = f"{address}/content?token={token}"
    data = {"url": url, 'setJavaScriptEnabled': False, 'gotoOptions': {'referer': 'https://www.google.com/'}}
    try:
        response = requests.post(request_url, headers=headers, json=data)
        content = response.text
        
    except Exception as e:
        content = ""    

    return content

# Função para tirar screenshot da página
def take_screenshot(url):
    request_url = f"{address}/screenshot?token={token}"
    data = {"url": url, "options": {"type": "jpeg","fullPage": False, "encoding": "base64" }}
    try:
        response = requests.post(request_url, headers=headers, json=data)
        screenshot = response.content
    except Exception as e:
        screenshot = None
    return screenshot

# Função para extrair dados estruturados
def extract_structured_data(content_raw, url):
    data = extruct.extract(content_raw, base_url=url, uniform=True)
    # og_data = extruct.extract(content_raw, base_url=url, syntaxes=['opengraph'], uniform=True)
    return data

# Função para extrair JSON-LD data
def extract_jld_data(content_raw, url):
    data = extruct.extract(content_raw, base_url=url, syntaxes=['json-ld'], uniform=True)
    return data

# Funcao para extrair open graph data
def extract_og_data(content_raw, url):
    data = extruct.extract(content_raw, base_url=url, syntaxes=['opengraph'], uniform=True)
    return data

# Função para baixar e converter a imagem og:image para base64
def download_and_convert_image(og_data):
    # data = json.loads(og_data)
    og_image_url = og_data['opengraph'][0]['og:image']
    if og_image_url:
        try:
            response = requests.get(og_image_url)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content))
            buffered = BytesIO()
            image.save(buffered, format="JPEG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            return img_base64
        except Exception as e:
            st.error(f"Erro ao baixar ou converter a imagem: {e}")
            return None
    else:
        st.info(og_image_url)
        st.warning("Imagem og:image não encontrada.")
        return None

# Função principal do Streamlit
def main():
    st.title("Scrape com Browserless")

    with st.form("indexer"):
        url = st.text_input("Enter the URL of the news article:", key="url")
        submitted = st.form_submit_button("Analisar link")

        if submitted:
            if not url:
                st.error("Please enter a URL.")
            else:
                with st.spinner("Loading..."):
                    content_raw = browserless_scrape(url)
                    str_data = extract_structured_data(content_raw, url)
                    og_data = extract_og_data(content_raw, url)
                    st.header("Result")
                    # st.subheader("Content")
                    # st.text_area("Content", content, key="content")
                    st.subheader("Raw Content")
                    st.text_area("Raw Content", content_raw, key="content_raw")
                    st.subheader("Main Content")
                    content = extract_content(url, content_raw)
                    st.text_area("Main Content",content, key="main_content")
                    st.subheader("Screenshot")
                    screenshot = take_screenshot(url)
                    if screenshot:
                        base64_image = base64.b64decode(screenshot)
                        st.image(base64_image, caption="Screenshot of the page", use_container_width=True)
                    else:
                        st.error("Failed to take screenshot.")
                    st.subheader("Open Graph Data")
                    st.json(og_data)
                    st.subheader("OG Image")
                    img_base64 = download_and_convert_image(og_data)
                    if img_base64:
                        st.image(f"data:image/jpeg;base64,{img_base64}", caption="Imagem og:image")
                    # if 'opengraph' in og_data and len(og_data['opengraph']) > 0 and 'og:image' in og_data['opengraph'][0]:
                        # st.image(og_data['opengraph'][0]['og:image'], caption="OG Image", use_container_width=True)
                    # else:
                        # st.error("No OG Image found.")
                    st.subheader("JSON-LD Data")
                    jld_data = extract_jld_data(content_raw, url)
                    st.json(jld_data)
                    st.subheader("Structured Data")
                    st.json(str_data)

if __name__ == "__main__":
    main()
