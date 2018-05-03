#CENSORSHIP ML ANALYSIS
#Edwin Gavis
#03-16-18

import collections
import jieba
import nltk
import numpy as np
import pandas as pd 
import sklearn
import sklearn.cluster as skcluster
import sklearn.decomposition as skdecomp
import sklearn.naive_bayes as sknb
import sklearn.linear_model as sklm
import sklearn.ensemble as sken
import urllib3

def get_stops():
	'''
	Retrieves opensourced Chinese stopwords list from Stopwords-ISO
	'''
	print('Getting Stops')
	http = urllib3.PoolManager()
	url = 'https://raw.githubusercontent.com/stopwords-iso/stopwords-zh/master/stopwords-zh.txt'
	r = http.request('GET', url)
	spaced_stops = r.data.replace(b'\n',b' ')
	l_stops = spaced_stops.decode('utf-8').split(' ')
	return l_stops

STOPS = get_stops() + ['\u200b', 'http', 'cn', 't', '示威', '集体行动', '反腐', '污染',
                       '这件', '这家', 'ASTA', '别向', 'VGV566', '展开','全文','c', 'vgv566',
                       'howowfeel']

PUNCTUATION = '“”>@【】（）[]！？；:《》，、。：./#'

#jieba & splitting
def j_split(l):
	rv = []
	for txt in l:
		split = jieba.cut(str(txt)) #Accurate cut, uses Markov models for unknown words
		depunctuator = str.maketrans('', '', PUNCTUATION)
		joined = " ".join(split).translate(depunctuator)
		rv.append(joined)	
	return rv

###

def latent_dirichlet(corpus):
	n_top_words = 10
	vect = sklearn.feature_extraction.text.CountVectorizer(stop_words = STOPS)
	dtm = vect.fit_transform(corpus)
	model = skdecomp.LatentDirichletAllocation(
		n_components=10, 
		max_iter=5,
        learning_method='online',
        learning_offset=50,
        random_state = 345678)
	model.fit(dtm)
	tf_feature_names = vect.get_feature_names()
	print_top_words(model, tf_feature_names, n_top_words)

def print_top_words(model, feature_names, n_top_words):
	print("LDA OUTPUT:")
	for i, topic in enumerate(model.components_):
		output = "Topic #{}: ".format(i)
		print(output)
		[print(feature_names[a])
         for a in topic.argsort()[:-n_top_words - 1:-1]]
	print()

###

def build_kmeans(corpus, df_, n_clust, verbose = False):
	'''
	'''
	vect = sklearn.feature_extraction.text.TfidfVectorizer(stop_words = STOPS)
	dtm = vect.fit_transform(corpus) 
	model = skcluster.KMeans(n_clusters = n_clust, random_state = 98765)
	model.fit(dtm)
	if verbose:
		centroids = model.cluster_centers_.argsort()[:,::-1]
		terms = vect.get_feature_names()
		for clust_num in range(n_clust):
			print('cluster ' + str(clust_num))
			for i in centroids[clust_num, :20]:
				print(terms[i])
	print()
	print(collections.Counter(model.labels_))
	alpha = []
	for index, val in enumerate(list(df_["censored"] == 1)):
		if val:
			alpha.append(model.labels_[index])
	print(collections.Counter(alpha))

###NOT USED IN CURRENT VERSION: 

def mult_nb():
	model = sknb.MultinomialNB()
	vect = sklearn.feature_extraction.text.CountVectorizer(stop_words = STOPS)
	dtm = vect.fit_transform(all_posts_txt)
	model.fit(dtm,
	          list(df["censored"] != 1))
	output = []
	for i, val in enumerate(model.coef_[0]):
		output.append((val,	vect.get_feature_names()[i]))
	print(sorted(output, reverse = True)[0:10])

###NOT USED IN CURRENT VERSION:

def elastic():
	model = sklm.ElasticNet(fit_intercept=True, l1_ratio=1, random_state=380410)
	vect = sklearn.feature_extraction.text.TfidfVectorizer(stop_words = STOPS)
	dtm = vect.fit_transform(all_posts_txt)
	model.fit(dtm,
	          [int(a) for a in list(df["censored"] != 1)])
	for i, coef in enumerate(model.coef_):
		if coef != 0:
			print("delta")

###

def random_forest(corpus, classifier):
	vect = sklearn.feature_extraction.text.TfidfVectorizer(stop_words = STOPS)
	dtm = vect.fit_transform(corpus)
	model = sken.RandomForestClassifier(random_state=2673)
	model.fit(dtm,
	          classifier)
	rf = []
	for i, val in enumerate(model.feature_importances_):
		rf.append((val, vect.get_feature_names()[i]))
	for score, word in sorted(rf, reverse=True)[0:10]:
		print(word)
		print(score)
		
###

#full pandas dataframe
df = pd.read_csv("queries_total.csv",encoding='utf-8')

#sub-dfs: 
q1 = '示威' #df.iloc[0]['query'].split(";")[0]
q1_df = df[df["query"].str.contains(q1) == True]
q2 = '集体行动'
q2_df = df[df["query"].str.contains(q2) == True]
q3 = '反腐'
q3_df = df[df["query"].str.contains(q3) == True]
q4 = '污染'
q4_df = df[df["query"].str.contains(q4) == True]

#corpora: 
all_posts_txt = list(df["content"])
all_censored_text = list(df[df['censored'] == 1]['content'])
all_noncensored_text = list(df[df['censored'] == 0]['content'])
q1_posts_txt = list(q1_df["content"])
q2_posts_txt = list(q2_df["content"]) 
q3_posts_txt = list(q3_df["content"]) 
q4_posts_txt = list(q4_df["content"]) 

[print(a) for  a in all_censored_text]

all_posts_txt = j_split(all_posts_txt)
all_censored_text = j_split(all_censored_text)
all_noncensored_text = j_split(all_noncensored_text)
q1_posts_txt = j_split(q1_posts_txt)
q2_posts_txt = j_split(q2_posts_txt)
q3_posts_txt = j_split(q3_posts_txt)
q4_posts_txt = j_split(q4_posts_txt)
'''
print("LDA")
latent_dirichlet(all_censored_text)
latent_dirichlet(all_noncensored_text)

print("KMEANS")
print("Q3")
#build_kmeans(q3_posts_txt, q3_df, 8, True)
print("Q4")
build_kmeans(q4_posts_txt, q4_df, 8, True)

#print("MULT-NB")
#mult_nb()

print("FOREST")
print("Q3")
random_forest(q3_posts_txt, list(q3_df["censored"] != 1))
print("Q4")
random_forest(q4_posts_txt, list(q4_df["censored"] != 1))
#random_forest(all_posts_txt, list(df["censored"] != 1))
'''

'''
Copyright (c) 2018 Edwin Gavis

Distributed under the MIT License:

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''