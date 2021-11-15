import scrapy
import json
import time


class PressreleasesSpider(scrapy.Spider):
    name = 'pressreleases'
    allowed_domains = ['www.dfs.ny.gov/reports_and_publications/press_releases/', 'dfs.ny.gov', 'dfs.ny.gov/reports_and_publications/press_releases/']
    start_urls = ['http://dfs.ny.gov/reports_and_publications/press_releases/']
    base_url = 'https://dfs.ny.gov/reports_and_publications/press_releases'
    temp_dict_contents = []
    count = 0

    def parse(self, response):
        rows = response.css('table tr')
        temp_dict_contents = {}
        for row in rows[1:]:
            scraped_info = {}
            #print(row.css('td').extract())
            #print(row.css('a::text').extract())
            row_temp1 = row.css('td::text').extract()
            date = row_temp1[0].rstrip()
            print(date)
            row_temp2 = row.css('a::text').extract()
            title = ""
            for j in row_temp2:
                temp_string = str(j)
                if temp_string == '\r\n':
                    title = title + temp_string.replace('\r\n', '.')
                elif temp_string.startswith('\r\n'):
                    title = title + temp_string.replace('\r\n', '')
                else:
                    title = title + temp_string.replace('\r\n','.')
            print(title)
            row_temp3 = row.css('a::attr(href)').extract()
            url = "https://dfs.ny.gov"+row_temp3[0]+"/"
            print(url)
            self.temp_dict_contents = self.temp_dict_contents
            scraped_info = {
                "date": date,
                "title": title,
                "url": url,
            }

            yield scraped_info
            #This below yield subrequest should normally work and get the contents of the url and paste it in the json file
            #but for some reason the request gets delayed and works in parallel and fetches the data randomly and pastes it
            #in the json file. So had to separate the contents into another json file
            yield scrapy.Request(url, callback=self.parse_subpage)

        NEXT_PAGE_SELECTOR = 'li.pager__item.pager__item--next a::attr(href)'
        next_page = response.css(NEXT_PAGE_SELECTOR).get()

        if next_page is not None:
            #next_page = response.urljoin(next_page)+'/'
            next_page_url = self.base_url + next_page
            print(next_page_url)
            yield scrapy.Request(next_page_url, callback=self.parse)

            #time.sleep(50)
            '''for j in row_temp2:
                print(j)'''
        '''else:
            with open('contents.json','w') as f:
                json.dump(self.temp_dict_contents,f)'''
    def parse_subpage(self, response):
        temp_url = response.url
        header_list = response.css(".page-body div h1::text").extract()
        header_str = str(header_list).replace('\\xa0', ' ')
        small_header_list = str(response.css(".page-body div h3 em::text").extract())
        if small_header_list is None:
            small_header_list = str(response.css(".page-body div h2::text").extract())
            if small_header_list is None:
                small_header_list = str(response.css(".page-body div h1::text").extract())
        small_header_str = small_header_list.replace('\\xa0', ' ')
        content_list = response.css(".page-body div p::text").extract()
        content_str = ""
        for i in content_list[3:]:
            content_str = content_str + str(i)
        final_content = str(header_str) + ' '+str(small_header_str) + ' '+(content_str)

        final_content1 = {}
        #have made this dictionary with key value as the url so that the mapping with the original json file becomes
        #easier and we can use this key-url to match with the value-url from the pressreleasesjson when giving the data
        #to the customer
        final_content1 = {temp_url: final_content}


        # if the subrequest wasn't delaying the below would have been the yield request
        #final_content1 = {"contents": final_content}
        #yield final_content1

        with open('contents.json', 'w') as f:
            json.dump(final_content1, f)






