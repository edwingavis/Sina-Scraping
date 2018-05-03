# -*- coding: utf-8 -*-

# Special Thanks to Xuzhou Yin 

import csv
import datetime
import progressbar
import time as systime
import urllib

from bs4 import BeautifulSoup
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.firefox.webdriver import FirefoxProfile
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

base_url = 'http://s.weibo.com/weibo/'
file_ = "output" + str(datetime.datetime.now().day) + "_" +str(datetime.datetime.now().hour) + "_"
file_index = 1

def scrape():
	global file_index
	with open('query.txt') as f:
		each_query = f.readlines()
	each_query = [x.strip() for x in each_query]
	for each in each_query:
		query = each
		s = each.split(';')
		keyword = s[0] #urllib.quote(urllib.quote(s[0]))
		date = s[1]
		page1 = s[2]
		page2 = s[3]
		scrap_each_query(keyword, date, page1, page2, query)
		file_index = file_index + 1
		print("sleeping - 10")
		systime.sleep(10)

def scrap_each_query(keyword, date, page1, page2, query):
	real_keyword = keyword
	keyword = urllib.parse.quote(urllib.parse.quote(keyword))
	all_content = []
	all_time = []
	all_links = []
	all_names = []
	home = str(Path.home())
	caps = DesiredCapabilities().FIREFOX
	caps["marionette"] = True
	caps["pageLoadStrategy"] = "none" 
	profile = FirefoxProfile(home + "/.mozilla/firefox/1qxjwpub.default")
	driver = webdriver.Firefox(profile, capabilities = caps)
	url = base_url + keyword + "&typeall=1&suball=1&timescope=custom:" + date + ":" + date + "&page=" + "1"
	print(url)
	driver.get(url)
	systime.sleep(5)
	bar = progressbar.ProgressBar()
	for i in bar(range(int(page1),int(page2) + 1)):
		url = base_url + keyword + "&typeall=1&suball=1&timescope=custom:" + date + ":" + date + "&page=" + str(i + 1)
		try:
			driver.get(url)
		except:
			systime.sleep(10)
			driver.get(url)
		try:
			page_source = driver.page_source
		except:
			break
		soup = BeautifulSoup(page_source, "lxml")
		#FOR COLLECTING FULL PAGE HTML: 
		#new_file = "html/query" + str(file_index) + "_" + str(i) + ".html" 
		#with open(new_file, "w") as file__:
		#	file__.write(str(soup))
		content = soup.findAll("p", { "class" : "comment_txt" })
		time = soup.findAll("a", { "class" : "W_textb" })
		for each in content:
			try:
				all_names.append(each['nick-name'])
			except KeyError:
				all_names.append("NA")
			all_content.append(each.get_text().replace("\n", ""))
		for each in time:
			try:
				all_links.append(each['href'])			
			except KeyError:
				all_links.append("NA")
			each = each.text
			time = ""
			if "月" in each:
				time = str(datetime.datetime.now().year) + "-" + each[0:each.index("月")] + "-" + each[(each.index("月") + 3):each.index("日")]
			else:
				try:
					time = each[0:each.index(" ")]
				except ValueError:
					time = each
			all_time.append(time)
		systime.sleep(15)
	driver.close()
	save_to_csv(file_ + str(file_index), real_keyword, date, all_content, all_names, all_links, query)

def save_to_csv(filename, keyword, date, content, names, links, query):
	with open("output/" + filename +'.csv', 'w') as csvfile:
	    spamwriter = csv.writer(csvfile, dialect='excel')
	    spamwriter.writerow(["query", "Post ID", "Post Content", "nickname", "link"])
	    for i in range(len(content)):
	    	spamwriter.writerow([query, i + 1, content[i], names[i], links[i]])

scrape()