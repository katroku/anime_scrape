import scrapy
from bs4 import BeautifulSoup
import requests


class AnimeSpider(scrapy.Spider):
    name = 'anime'

    start_urls = ['https://www.anime-planet.com/anime/top-anime?page=1']

    def parse(self, response):
        #anime_page_links = response.css('td.tableTitle a')
        anime_page_links = response.xpath('//td[@class="tableTitle"]//a[@class="tooltip"]')
        yield from response.follow_all(anime_page_links, self.parse_anime)

        pagination_links = response.css('li.next a')
        yield from response.follow_all(pagination_links, self.parse)


    def parse_anime(self, response):

        root_url = "anime-planet.com"

        tags_arr = response.xpath('//div[@class="tags "]//a/text()').getall()
        tags_str = ('|').join([tag.strip('\n') for tag in tags_arr])

        contentWarning_arr = response.xpath('//div[@class="tags tags--plain"]//a/text()').getall()
        contentWarning_str = ('|').join([tag.strip('\n').strip(',') for tag in contentWarning_arr])

        altTitle = response.xpath('//h2[@class="aka"]/text()').get()
        #NoneType object cannot strip and will raise error (see Terminal Output Error)
        altTitle = altTitle.strip('\n') if altTitle!=None else None

        anime_data = {
            'title': response.xpath('//h1[@itemprop="name"]/text()').get(),
            'altTitle': altTitle,
            'medium': response.xpath('//span[@class="type"]/text()').get().split('\n')[0],
            'numEpisodes': response.xpath('//span[@class="type"]/text()').get().split('\n')[1],
            'studios': response.xpath('//a[contains(@href,"/studios")]/text()').get(),
            'season': response.xpath('//div[@id="siteContainer"]//a[contains(@href,"anime/seasons")]/text()').get(),
            'year' : response.xpath('//div[@id="siteContainer"]//span[@class="iconYear"]/text()').get().strip(),
            'avgRating': response.xpath('//div[@class="avgRating"]/@title').get(),
            'rank': response.xpath('//div[@class="pure-1 md-1-5"]/text()').getall()[-1].strip('\n'),
            'description': (' ').join(response.xpath('//div[@class="pure-1 md-3-5"]//p/text()').getall()),
            'tags': tags_str,
            'contentWarning': contentWarning_str,
            'image': root_url + response.xpath('//img[@itemprop="image"]/@src').get(),
        }

        stats_id = response.xpath('//section[@class="sidebarStats"]/@data-id').get()
        stats_name = response.xpath('//section[@class="sidebarStats"]/@data-url-slug').get()
        stats_data_og = response.xpath('//section[@class="sidebarStats"]/@data-og').get()
        if (stats_id and stats_name) is not None:
            link = f"https://www.anime-planet.com/ajaxDelegator.php?mode=short_stats&type=anime&id={stats_id}&url={stats_name}&og={stats_data_og}"
            res = requests.get(link)
            soup = BeautifulSoup(res.text,'html.parser')
            count = 0
            for i in soup.find_all('li'):
                data_str = i.text.strip('\n').split('\n')
                anime_data[data_str[1]] =  data_str[0]             

        yield anime_data