#OPENS FILES!

from bs4 import BeautifulSoup

def open_file(filename):
	with open("html/" + filename, "r") as file_:
		file__ = file_.read().encode('ascii','ignore')
		soup = BeautifulSoup(file__, "lxml")
		print(soup)
		content = soup.findAll("p")
		#content = soup.findAll("p", { "class" : "comment_txt" })
		#print(content)
		'''
		all_names = []
		for each in content:
			try:
				all_names.append(each['nick-name'])
			except KeyError:
				all_names.append("NA")
			#all_content.append(each.get_text().replace("\n", ""))
	print(all_names)
	'''

open_file("query1_2.html")