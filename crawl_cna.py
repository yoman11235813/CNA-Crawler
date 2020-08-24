import os
import requests
from bs4 import BeautifulSoup
import numpy as np 
import pandas as pd
import time
import random

# dates = []
# links = []
year = '2020'
month = '1'
index_file = "./output/{}/index.csv".format(year)

def check_url():
	urls = pd.read_csv(index_file).LINK.tolist()
	id_list = [i.split('/')[-1].split('.')[0] for i in urls]
	create_url(id_list)

def create_url(id_list):
	months = month if len(month) == 2 else "0" + month
	days = 30 if months == "02" else 31 if months in {"04","06","09","11"} else 32
	for j in range(1,days):
		links = []
		counter = 0
		day = str(j) if j > 9 else "0" + str(j)
		print(day)
		# dates.append(year + months + day)
		for j in range(5001,5021):
			index = str(j) 
			url = "https://www.cna.com.tw/news/aspt/" + year + months + day + index + ".aspx"
			if not year + months + day + index in id_list:
				links.append(url)
		for j in range(1,1001):
			index = "0" + str(j) if j > 99 else "00" + str(j) if j > 9 else "000" + str(j) 
			url = "https://www.cna.com.tw/news/aspt/" + year + months + day + index + ".aspx"
			if not year + months + day + index in id_list:
				links.append(url)

		get_data(links, counter)

def get_data(links, counter):
	for url in links:
		try:
			article = requests.get(url)
		except Exception as e:
			print(e)
			continue
		
		soup = BeautifulSoup(article.content, 'html.parser')
		title = soup.find('meta', {'property':'og:title'}).get('content').rsplit(' | ')[0]
		pay = ''
		try:
			pay = soup.find('div', class_='paragraph').find('a').text
		except:
			pass

		if title == '404': 
			counter += 1
			if counter > 30: break
			continue
		if pay == '付費會員': continue
		counter = 0
		print(url)
		print(title)
		date = url.rsplit('/',1)[1].rsplit('.')[0][4:8]
		number = url.rsplit('/',1)[1].rsplit('.')[0][8:12]

		df = pd.DataFrame(data = [{'TITLE':title,
									'TIME':soup.find('meta', {'itemprop':'dateCreated'}).get('content'),
									'SECTION':soup.find('meta', {'property':'og:title'}).get('content').rsplit(' | ')[1],
									'KEYWORDS':soup.find('meta', {'name':'keywords'}).get('content'),
									'LINK':soup.find('meta', {'property':'og:url'}).get('content')}],
						   columns = ['TITLE', 'TIME', 'SECTION', 'KEYWORDS', 'LINK'])
		pd.set_option("display.max_columns", None, "display.max_colwidth", -1)
		df.to_csv(index_file, mode='a', index = False, header=False)
		# data_list.append(ndf)
		# print(data_list)
		
		body = soup.find_all('div', class_='paragraph')
		x = body[0].find_all('p')
		
		list_paragraphs = []
		for p in np.arange(0, len(x)):
			paragraph = x[p].get_text()
			list_paragraphs.append(paragraph)
			final_article = " ".join(list_paragraphs)

		filename = "./output/{}/{}/{}.txt".format(year,date,number)
		os.makedirs(os.path.dirname(filename), exist_ok=True)
		with open(filename, "w") as f:
			f.write('{}\n{}'.format(title,final_article))

		time.sleep(random.randint(0,2))

if os.path.isfile(index_file):
	check_url()

else:
	os.makedirs(os.path.dirname(index_file), exist_ok=True)
	df = pd.DataFrame(columns = ['TITLE', 'TIME', 'SECTION', 'KEYWORDS', 'LINK'])
	pd.set_option("display.max_columns", None, "display.max_colwidth", -1)
	df.to_csv(index_file, mode='w', index = False, header=True)

	check_url()



