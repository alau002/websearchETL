#import libraries
import webbrowser
import inquirer 
import requests 
from bs4 import BeautifulSoup
import mysql.connector


#define dictionary to store search options: Google, Bing, Yahoo, DuckDuckGo 
engines = {'Bing':'https://www.bing.com/search?q=',
        'Google':'http://google.com/search?q=',
        'Yahoo':'https://search.yahoo.com/search?p=',
        'DuckDuckGo':'https://html.duckduckgo.com/html/?q='}

#block list to clean up search results 
block_list = ['https://www.bing.com/new/termsofuse','https://privacy.microsoft.com/en-us/privacystatement',
              'help.ads.microsoft','https://help.ads.microsoft.com','https://account.microsoft.com/account/privacy',
              'https://creativecommons.org/licenses/by-sa/3.0','http://go.microsoft.com/fwlink/',
              'https://go.microsoft.com/fwlink','https://support.microsoft.com','http://support.google.com',
              'http://policies.google.com','https://accounts.google.com','http://www.google.com/preferences',
              'setprefs?hl=en&prev=','https://search.yahoo.com/preferences','https://mail.yahoo.com/?.src=ym',
              'https://www.yahoo.com/news','https://finance.yahoo.com','https://sports.yahoo.com/fantasy',
              'https://sports.yahoo.com','https://shopping.yahoo.com','https://www.yahoo.com/news/weathe',
              'https://www.yahoo.com/lifestyle','https://help.yahoo.com/kb/search-for-desktop','http://maps.google.com/maps',
              'https://login.yahoo.com?.src=search','https://images.search.yahoo.com/search','https://video.search.yahoo.com/search',
              'https://search.yahoo.com/search?ei=UTF-8&','https://yahoo.uservoice.com/forums','https://legal.yahoo.com/',
              'https://guce.yahoo.com/privacy-dashboard','https://advertising.yahoo.com','https://help.yahoo.com','https://www.yahoo.com'
             ]

#provide search engine options for user
engine_options = [inquirer.List('Search Engine',
                message="Choose Search Engine:",
                choices=['Google', 'Bing', 'Yahoo', 'DuckDuckGo'],),]
engine = inquirer.prompt(engine_options)['Search Engine']

#prompt user to input web search query 
input_query= raw_input("Enter search query: ")

#new browser tab will be opened if possible 
new=2
#display url with the above parameters 
webbrowser.open(engines[engine]+input_query,new=new)

#request html from web search 
r = requests.get(engines[engine]+input_query, headers={'user-agent': 'my-app/0.0.1'})

#add try catch for errors 
#trycatch 

#create beautifulsoup object 
soup = BeautifulSoup(r.text, 'html.parser')

#filter function to clean up url scrap results 
def filter_function(url,block_list):
    if 'http' not in url:
        return False
    elif any(blocked in url for blocked in block_list):
        return False
    else:
        return True

#additional data transformations for google searches 
def google_transformer(url):
    return url.split('&sa=')[0]

#function for finding urls resulted from search, with associated html clean up and filtering 
#return list of cleaned up url 
def urls(soup,engine):
    #find <a> tages used for links, where tags have href attribute from soup object
    all_href = map(lambda x: x.get('href'),soup.find_all('a',href=True))
    #filter to url links 
    url = filter(lambda x: filter_function(x,block_list), all_href)
    #additional filter for google searches
    if engine=='Google':
        url = map(google_transformer,url)
    #return cleaned up list of urls 
    return list(map(str,map(lambda x: x.strip('/url?q='),url)))

#opening connection to MySQL database 
connection = mysql.connector.connect(user='root', database = 'MY_CUSTOM_BOT', password = '')
#creating cursor handler for inserting data 
cursor = connection.cursor()

#query for adding search info
add_search = ('INSERT INTO searches(query,engine) values(%(query)s, %(engine)s)')
#function query for adding url info 
def add_url(table,url,f_key):
    query = ('INSERT INTO %(table)s(url,search_id) values(\'%(url)s\',%(f_key)s)')
    return query%{'table':table,'url':url,'f_key':f_key}


#inserting search info 
cursor.execute(add_search,{'query':input_query, 'engine':engine})
#obtain last row id of the search table to insert into foreign keys
last_search_id = cursor.lastrowid

#inserting url info
for url in urls(soup):
    tables = {'Bing':'bing_urls', 'Google':'google_urls', 'Yahoo':'yahoo_urls','DuckDuckGo':'duckduckgo_urls'}
    cursor.execute(add_url(tables[engine],url,last_search_id))

#print(soup)

#commit data to database 
connection.commit()

#closing cursor and connection 
cursor.close()
connection.close()