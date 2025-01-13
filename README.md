# Streamlit App AI Scrapy com Firecrawl

Este é uma colecao de aplicacoes [Streamlit](https://streamlit.io) que fazem uso de tecnologias de Scrapy como Firecrawl, Selenium, BeatfulSop e ferramentas de IA para extracao, sumarizacao e manipulacao de dados.

## Tecnologias

Algumas das principais ferramentas e tecnologias utilizadas foram:

**Framework**

* [Streamlit](https://streamlit.io)

**Bibliotecas**

* Extruct
* beautifulsoup
* w3lib
* selenium
* nodriver
* requests
* ~~pandas~~
* firecrawl-py

**IA**

* [Cloudflare Workers AI](https://developers.cloudflare.com/workers-ai/)


## Instalacao

Copie [.streamlit/secrets.toml.example](./.streamlit/secrets.toml.example) para `.streamlit/secrets.toml`. Este arquivo conterá todos os segredos e chaves de API necessários para executar o aplicativo.

Instale as dependências do Python:

```bash
python -m venv venv
source ./venv/bin/activate
python -m pip install -r requirements.txt
```

## Executando

Para executar o aplicativo, use o seguinte comando:

```bash
python -m streamlit run app.py
```