# description: naver blog 오늘자 올라온 글 가져오기
# author: jmj

# import requests
# from urllib.request import urlopen
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
# from bs4 import BeautifulSoup

import feedparser
from konlpy.utils import pprint
from time import mktime
from datetime import datetime, timedelta

import ssl

# naver blog 의 경우 전체 카테고리이어야 한다. -> 네이버 아이디를 받아서 연결시켜 주던지, 아이디만 추출해서 넣던지.
# 목록 닫기일 경우 못가져오니 목록 열기까지 해주고 가져와야 한다.
naver_blog_list = [
     'http://blog.naver.com/PostList.nhn?blogId=laonple' # 라온피플
    ,'https://blog.naver.com/nu4345'
    ,'https://blog.naver.com/PostList.nhn?blogId=nu4345'
]

naver_blog_rss_list = [
    'https://laonple.blog.me/rss'
]

# youtube 최신 동영상
youtube_list = [
     'https://www.youtube.com/channel/UCcIXc5mJsHVYTZR1maL5l9w' + '/videos' # deeplearning ai
    ,'https://www.youtube.com/channel/UCTivi6Kji_93AjJu-7-osLQ' + '/videos' # idea factory kaist
    ,'https://www.youtube.com/user/hunkims' + '/videos' # sung kim
]


# naver blog
# - rss 로 가져오기
# - rss 가 아닌 경우도 가져오기
# youtube 

# site_type
#   0 : naver blog
#   1 : youtube

site_type = 0
use_rss = 1     # 0: not use rss, use site url, 1: use rss
last_crawled_date = datetime(2020, 6, 1, 23, 59, 59)

# dict in list [ {} ]

crawled_list = []



def crawling_naver_blog():
    current_crawl_url = naver_blog_list[0]

    driver = webdriver.Chrome('./chromedriver')

    if hasattr(ssl, '_create_unverified_context'):
            ssl._create_default_https_context = ssl._create_unverified_context 

    if use_rss:

        current_crawl_url = naver_blog_rss_list[0]
        # rss 로 내용 가져오기
        data = feedparser.parse(current_crawl_url)
        for entry in data.entries:
            # published date 와 last_crawled_date 비교: datetime <
            # 이후 일 경우만 namedtuple에 저장.
            # sort
            if datetime.fromtimestamp(mktime(entry['published_parsed'])) > last_crawled_date:
                # print('published_parsed : {}'.format(entry['published_parsed']))
                # title, link, description, image_link, published_Datetime, crawled_dateteime
                entry_dict = {}
                entry_dict['title'] = entry['title']
                entry_dict['link'] = entry['link']
                entry_dict['description'] = entry['description'] # 100자만 가져오기
                entry_dict['published_datetime'] = datetime.fromtimestamp(mktime(entry['published_parsed']))
                entry_dict['crawled_datetime'] = datetime.now()

                # image link 직접 들어가서 가져오기..
                # entry_dict['image_link'] = entry['title']
                driver.get(entry_dict['link'])
                #driver.get('https://blog.naver.com/genycho?Redirect=Log&logNo=221978038485&proxyReferer=https%3A%2F%2Fsearch.naver.com%2Fsearch.naver%3Fquery%3Dselenium%26where%3Dpost%26sm%3Dtab_nmr%26nso%3D')
                # driver.get('https://blog.naver.com/tramper2/221979760263')
                # 썸네일이 있는 경우
                # 제목 부분에 썸네일이 있는 경우
                # 없는 경우
                try:
                    entry_dict['image_link'] = driver.find_element_by_class_name('se-title-cover').value_of_css_property('background-image')[5:-2]
                except NoSuchElementException:
                    # 스마트에디터
                    driver.switch_to.frame(driver.find_element_by_name("mainFrame"))
                    if len(driver.find_elements_by_id('postViewArea')) == 0:
                        # 스마트 에디터인데 썸네일이 없는 경우
                        try:
                            entry_dict['image_link'] = driver.find_elements_by_id('postListBody')[0].find_element_by_xpath('.//div[@class="se-main-container"]//img').get_attribute('src')
                        except NoSuchElementException:
                            # 이미지가 없음
                            entry_dict['image_link'] = ""
                    # 스마트에디터가 x
                    else:
                        entry_dict['image_link'] = driver.find_elements_by_id('postViewArea')[0].find_element_by_xpath('.//img').get_attribute('src')

                # 썸네일이 없는 경우

                crawled_list.append(entry_dict)
            else:
                break

        # for i in crawled_list:
        #     print('title: {}\n, link: {}\n, published_datetime: {}\n, crawled_datetime: {}\n'.format(
        #         i['title'], i['link'], i['published_datetime'], i['crawled_datetime']))
    else:
        # site 들어가서 내용 가져오기
        driver.get(naver_blog_list[2])

        # 목록 닫기라고 text 가 되어있어야 가져올 수 있음
        span = driver.find_element_by_id('toplistSpanBlind')
        
        if span.text == '목록열기':
            driver.find_element_by_class_name('btn_openlist').click()

        table = driver.find_element_by_class_name('blog2_list')
        # 1초 주기
        # title
        all_children_by_xpath = table.find_elements_by_xpath(".//td//a")
        all_children_by_xpath_date = table.find_elements_by_xpath(".//td[@class='date']")

        title_list = []
        date_list = []

        # 1페이지에 10개인데, 10개 일때도 -시간 전 일 경우 페이지 2로 넘어가야된다~
    
        for date in all_children_by_xpath_date:
            if not date.text.startswith(str(last_crawled_date.year)):
                date_list.append(date.text)
            else:
                break

        index = 0
        for title in all_children_by_xpath:
            if index >= len(date_list):
                break

            title_list.append(title.text)
            entry_dict = {}
            entry_dict['title'] = title.text
            entry_dict['link'] = title.get_attribute('href')

            crawled_list.append(entry_dict)
            index += 1

        index = 0
        for crawled_data in crawled_list:

            driver.get(crawled_data['link'])
                
            if '시간 전' in date_list[index]:
                date_prev_time = int(date_list[index].split('시간 전')[0])
                crawled_data['published_datetime'] = datetime.now() - timedelta(hours=date_prev_time)

            # entry_dict['published_datetime'] = datetime.fromtimestamp(mktime(entry['published_parsed']))
            
            crawled_data['image_link'] = driver.find_element_by_class_name('se-title-cover').value_of_css_property('background-image')[5:-2]
            crawled_data['description'] = driver.find_element_by_class_name('se-main-container').text[:100]
            crawled_data['crawled_datetime'] = datetime.now()


    

def main():
    if site_type == 0:
        # naver blog rss 가져오기
        crawling_naver_blog()


if __name__ == "__main__":
    main()

# 해야할 것
# selenium delay 적용 후 테스트
# naver 전체 카테고리 선택되도록 url 조정
# youtube crawling