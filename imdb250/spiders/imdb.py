import scrapy
import logging
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from requests_html import HTMLSession

class ImdbSpider(scrapy.Spider):
    name = "imdb"
    allowed_domains = ["toscrape.com"]
    start_urls = ["https://books.toscrape.com/catalogue/category/books_1/index.html"]

    def start_requests(self):
        session = HTMLSession()

        # Tentar a conexão ao site
        try:
            response = session.get(self.start_urls[0])
            response.raise_for_status()  

            title = response.html.find("title", first=True).text
            url = response.url

            logging.info("Application title is %s", title)
            logging.info("Application URL is %s", url)

      
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            navegador = webdriver.Chrome(options=chrome_options)
            navegador.maximize_window()
            navegador.get(self.start_urls[0])
            logging.info("Application title is %s", navegador.title)
            logging.info("Application URL is %s", navegador.current_url)

            time.sleep(2)

            yield scrapy.Request(url=navegador.current_url, callback=self.parse)
        except Exception as e:
            logging.error("Failed to fetch the webpage: %s", e)

    def parse(self, response):
        link_livros = response.css('.product_pod h3 a::attr(href)').getall()

        for link in link_livros:
            url = response.urljoin(link)
            yield scrapy.Request(url=url, callback=self.parse_livro)

    def parse_livro(self, response):
        descricao = response.css('#product_description + p::text').get()
        titulo = response.css('h1::text').get()
        preco = response.css('.price_color::text').get()

        logging.info("Título do Livro: %s", titulo)
        logging.info("Descrição: %s", descricao)
        logging.info("Preço: %s", preco)

        objeto_com_valores = {
            "titulo": titulo,
            "descricao": descricao,
            "preco": preco
        }
        
        self.save_to_json(objeto_com_valores)



    def save_to_json(self, item):
        # Adicionar o item ao arquivo JSON
        with open('dados.json', 'a') as json_file:
            json.dump(item, json_file)
            json_file.write('\n')
