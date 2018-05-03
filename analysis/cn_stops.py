import urllib3

def get_stops():
    '''
    '''
    print('Getting Stops')
    http = urllib3.PoolManager()
    url = 'https://raw.githubusercontent.com/stopwords-iso/stopwords-zh/master/stopwords-zh.txt'
    r = http.request('GET', url)
    cleaned_stops = r.data.replace(b"\n",b" ").decode('utf-8')
    return cleaned_stops

print(get_stops().split(" "))