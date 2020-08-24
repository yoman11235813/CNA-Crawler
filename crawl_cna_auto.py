import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import schedule
import datetime
from threading import Thread 
import os
import random

# last_update_time = (datetime.datetime.today() - datetime.timedelta(days=1))
current_time = datetime.datetime.today()
print ("開始時間： " + str(current_time))
# index_file = "./output/{}/index.csv".format(last_update_time.year)

def create_index_file(new_index_file):
    os.makedirs(os.path.dirname(new_index_file), exist_ok=True)
    df = pd.DataFrame(columns = ['TITLE', 'TIME', 'SECTION', 'KEYWORDS', 'LINK'])
    pd.set_option("display.max_columns", None, "display.max_colwidth", -1)
    df.to_csv(new_index_file, mode='w', index = False, header=True)

def get_coverpage():
    url = 'https://www.cna.com.tw/list/aall.aspx'
    r1 = requests.get(url)

    soup1 = BeautifulSoup(r1.content, 'html.parser')
    coverpage_news = soup1.find('ul', class_='mainList').find_all('li')

    return get_data(coverpage_news)

def get_data(coverpage_news):
    year = coverpage_news[0].find('a')['href'].rsplit('/',1)[1].rsplit('.')[0][0:4]
    # month = coverpage_news[0].find('a')['href'].rsplit('/',1)[1].rsplit('.')[0][4:6]
    new_index_file = "./output/{}/index.csv".format(year)
    if not os.path.isfile(new_index_file): create_index_file(new_index_file)

    last_update = datetime.datetime.today()
    number_of_articles = len(coverpage_news)
    links = pd.read_csv(new_index_file).LINK.tolist()

    for n in range(0, number_of_articles):
        
        if "/news/" not in coverpage_news[n].find('a')['href']: continue
        
        link = coverpage_news[n].find('a')['href']
        if link in links: break

        # news_published = coverpage_news[n].find('div', class_='date').get_text()
        # news_date = news_published.rsplit(' ')[0].rsplit('/')
        # news_time = news_published.rsplit(' ')[1].rsplit(':')
        # # print(news_date)
        # # print(news_time)
        # news_published = datetime.datetime(int(news_date[0]), int(news_date[1]), int(news_date[2]), int(news_time[0]), int(news_time[1]))

        # if news_published <= last_update_time: break

        title = coverpage_news[n].find('h2').get_text()
        article = requests.get(link)
        soup_article = BeautifulSoup(article.content, 'html.parser')
        df = pd.DataFrame(data = [{'TITLE':title,
                                    'TIME':soup_article.find('meta', {'itemprop':'dateCreated'}).get('content'),
                                    'SECTION':soup_article.find('meta', {'property':'og:title'}).get('content').rsplit(' | ')[1],
                                    'KEYWORDS':soup_article.find('meta', {'name':'keywords'}).get('content'),
                                    'LINK':soup_article.find('meta', {'property':'og:url'}).get('content')}],
                           columns = ['TITLE', 'TIME', 'SECTION', 'KEYWORDS', 'LINK'])
        pd.set_option("display.max_columns", None, "display.max_colwidth", -1)
        df.to_csv(new_index_file, mode='a', index = False, header=False)

        body = soup_article.find_all('div', class_='paragraph')
        final_article = ' '.join(i.text for i in body[0].find_all('p'))

        print(link)
        print(title)

        news_id = link.rsplit('/',1)[1].rsplit('.')[0]
        year = news_id[0:4]
        date = news_id[4:8]
        number = news_id[8:12]
        # print(news_id,year,date,number)

        filename = "./output/{}/{}/{}.txt".format(year,date,number)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
            f.write('{}\n{}'.format(title,final_article))

        time.sleep(random.randint(0,2))

    print("最後更新： " + str(last_update))
    # return last_update

# def crawl():
#     global last_update_time
#     last_update_time = get_coverpage()

# schedule.every().hour.do(crawl)
schedule.every().day.at("00:00").do(get_coverpage)
schedule.every().day.at("09:00").do(get_coverpage)
schedule.every().day.at("12:00").do(get_coverpage)
schedule.every().day.at("15:00").do(get_coverpage)
schedule.every().day.at("18:00").do(get_coverpage)
schedule.every().day.at("21:00").do(get_coverpage)

if __name__ == '__main__':

    # if not os.path.isfile(index_file):
    #     create_index_file(index_file)
        
    while True:
        schedule.run_pending()  
        time.sleep(1)


