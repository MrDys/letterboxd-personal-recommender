import scrapy
import scrapydo
import json
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy import Item, Field

class FilmItem(Item):
    id = Field()
    name = Field()
    url = Field()
    rating = Field()
    heart = Field()


class FilmSpider(CrawlSpider):
    name = "film_spider"
    allowed_domains = ['letterboxd.com']
    rules = [Rule(LinkExtractor(allow=['films/page']), callback='parse_item', follow=True)]

    # Parses out the id, link, name, rating, and heart status for a user's movies
    def parse_item(self, response):
        for id in response.css('li.poster-container'):
            identifier = id.css('::attr(data-film-id)').get()
            link = id.css('::attr(data-target-link)').get()
            name  = id.css('::attr(alt)').get()
            try:
                rating = id.css('p.poster-viewingdata span.rating').css('::attr(class)').re(r'\brated-(\d+)\b')[0]
            except IndexError:
                rating = 0
            if id.css('p.poster-viewingdata span.like').get() != None:
                heart = 1
            else:
                heart = 0

            item = FilmItem()
            item["id"] = int(identifier)
            item["name"] = name
            item["url"] = link
            item["rating"] = int(rating)
            item["heart"] = heart

            yield item


def lambda_handler(event, context):
    # Set up variables and grab the initial page
    user = event['queryStringParameters']['user']
    url = 'https://letterboxd.com/' + user + '/films/page/1'

    # Set up the Scrapy spider and crawl through the pages
    scrapydo.setup()
    items = scrapydo.run_spider(FilmSpider, start_urls=[url])
    
    jsonText = '[';
    for item in items:
        jsonText += json.dumps(dict(item)) + ","
    
    jsonText = jsonText[:-1]
    jsonText += ']'
    
    return jsonText
