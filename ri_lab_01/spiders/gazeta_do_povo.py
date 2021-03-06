# -*- coding: utf-8 -*-
import scrapy
import json
from datetime import datetime
from ri_lab_01.items import RiLab01Item


class GazetaDoPovoSpider(scrapy.Spider):
    name = 'gazeta_do_povo'
    allowed_domains = ['gazetadopovo.com.br']
    start_urls = []

    def __init__(self, *a, **kw):
        super(GazetaDoPovoSpider, self).__init__(*a, **kw)
        with open('seeds/gazeta_do_povo.json') as json_file:
            data = json.load(json_file)
        self.start_urls = list(data.values())

    def parse(self, response):
        secoes = ["republica", "mundo", "educacao", "economia", "republica/2/"]
        for secao in secoes:
            yield response.follow(response.url + secao, self.parse_per_section)
        page = response.url.split("/")[-2]
        filename = 'quotes-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)

    def parse_per_page(self, response):
        subtitle = response.css("div.c-overhead ::text").extract_first()
        title = response.css("h1.c-title ::text").extract_first().encode("utf-8")
        date = response.css("div.c-credits li:nth-child(3) ::text").extract_first()
        author = response.css("div.c-credits li:nth-child(1) ::text").extract_first()
        section = response.css("li.c-title-content a ::text").extract_first()

        url = response.url
        if date is None or date[0] != "[":
            date = response.css("div.c-credits li:nth-child(2) ::text").extract_first()

        date = datetime.strptime(str(date[1: 11]), '%d/%m/%Y')

        all_p = response.css("div.paywall-google p ::text")
        text = ""
        for p in all_p:
            text += p.extract().encode("utf-8")
        text = text.replace(',', '')
        itemLab = RiLab01Item(title=title, author=author, url=url, sub_title=subtitle.capitalize(), date=date, section=section,
                              text=text)
        yield itemLab

    def parse_per_section(self, response):
        for article in response.css("article"):
            link = article.css("div.c-box-description h2 a::attr(href)").extract_first()
            yield response.follow(link, self.parse_per_page)
