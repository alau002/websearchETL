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

#create beautifulsoup object 
soup = BeautifulSoup(r.text, 'html.parser')

#function for finding urls resulted from search, with associated html clean up and filtering 
#return list of cleaned up url 
def urls(soup):
    #find <a> tages used for links, where tags have href attribute from soup object
    all_href = map(lambda x: x.get('href'),soup.find_all('a',href=True))
    #filter to url links 
    url = filter(lambda x: 'http' in x, all_href)
    #return cleaned up list of urls 
    return list(map(lambda x: x.strip('/url?q='),url))

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


#commit data to database 
connection.commit()

#closing cursor and connection 
cursor.close()
connection.close()