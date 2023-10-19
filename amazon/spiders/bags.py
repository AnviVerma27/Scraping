import scrapy
from urllib.parse import urljoin
import csv

class BagsSpider(scrapy.Spider):
    name = "bags"


    def __init__(self):
        with open('results.csv','w') as csv_file:
            csv_file.write('product_title,price,rating,num_reviews,ASIN,manufacturer\n')

    def start_requests(self):
        keyword = 'bags'
        url = f"https://www.amazon.in/s?k={keyword}&page=1"
        yield scrapy.Request(url = url, callback=self.parse, meta={'keyword':keyword, 'page':1})

    def parse(self, response):
        page = response.meta['page']
        keyword = response.meta['keyword']

        search_products = response.css("div.s-result-item[data-component-type=s-search-result]")

        for product in search_products:
            product_url_relative = product.css("a.a-link-normal.s-no-outline::attr(href)").get()
            product_url = urljoin("https://www.amazon.in",product_url_relative).split("?")[0]
            yield scrapy.Request(url= product_url, callback= self.parse_product_data, meta={'keyword':keyword, 'page':1})


        if page == 1:
            available_pages = response.xpath('//*[contains(@class, "s-pagination-item")]/text()').getall()
            print(available_pages)

            last_page = available_pages[4]
            for page_num in range(2, int(last_page)):
                amazon_search_url = f'https://www.amazon.in/s?k={keyword}&page={page_num}'
                yield scrapy.Request(url=amazon_search_url, callback=self.parse, meta={'keyword': keyword, 'page': page_num})

    def parse_product_data(self,response):
        items =  {
                "product_title" : response.xpath("normalize-space(//span[@id='productTitle']/text())").get(),
                "price": response.xpath("//span[@class='a-price-whole'][1]/text()").get(),
                "rating": response.xpath("normalize-space(//a[@class='a-popover-trigger a-declarative']/span[@class='a-size-base a-color-base']/text())").get(),
                "num_reviews": response.xpath("//span[@id='acrCustomerReviewText']/text()").get(),
                "ASIN": response.xpath("//div[@id='detailBullets_feature_div']/ul/li[4]/span/span[2]/text()").get(),
                "manufacturer": response.xpath("//div[@id='detailBullets_feature_div']/ul/li[8]/span/span[2]/text()").get()
            }


        with open('results.csv','a') as csv_file:
                writer = csv.DictWriter(csv_file,fieldnames=items.keys())
                writer.writerow(items)    

        
