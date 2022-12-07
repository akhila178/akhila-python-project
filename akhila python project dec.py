#!/usr/bin/env python
# coding: utf-8

# In[2]:


from bs4 import BeautifulSoup
import requests
import pandas as pd 


# In[3]:


needed_headers = {'User-Agent': "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"}
response = requests.get("https://www.themoviedb.org/movie")


# In[4]:


response.status_code


# In[5]:


dwn_content = response.text
len(dwn_content)


# In[7]:


dwn_content[:500]


# In[8]:


test_doc = BeautifulSoup(response.text, 'html.parser')


# In[9]:


type(test_doc)


# In[10]:


test_doc.find('title')


# In[11]:


test_doc.find('img')


# In[12]:


def get_page_content(url):
    # In this case , we are going to give request.get function headers to avoid the Status code Error 403

    get_headers = {'User-Agent': "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"}
    response_page = requests.get(url, headers = get_headers )
    # we are going to raise exception here if status code gives any value other than 200.
    if not response_page.ok:
        raise Exception ("Failed to request the data. Status Code:- {}".format(response_page.status_code))
    else:
        page_content = response_page.text
        doc_page = BeautifulSoup(page_content, "html.parser")
        return doc_page


# In[13]:


popular_shows_url = "https://www.themoviedb.org/movie"
doc = get_page_content(popular_shows_url)


# In[14]:


doc.title.text


# In[15]:


doc.find_all('div', {'class': 'card style_1'})[0].h2.text


# In[18]:


doc.find_all('div', {'class': 'user_score_chart'})[0]['data-percent']


# In[23]:


def empty_dict():
    scraped_dict = {  
                    'Title': [],
                    'User_rating': [], 
                    'Release_date':[], 
                    'Genre': [],
                    'Director': [], 
                     'Cast': []        
                    }
    return scraped_dict


# In[24]:


def user_score_info(tag_user_score, i, scraped_dict):
    if tag_user_score[i]['data-percent'] == '0':
        scraped_dict['User_rating'].append('Not rated yet')
    else:
        scraped_dict['User_rating'].append(tag_user_score[i]['data-percent'])


# In[25]:


doc.find_all('div', {'class': 'card style_1'})[0].h2.a['href']


# In[26]:


def get_show_info(doc_page):
    base_link_1 = "https://www.themoviedb.org"
    tag_title = tag_premired_date = tag_shows_page = doc_page.find_all('div', {'class': 'card style_1'})
    tag_user_score = doc_page.find_all('div', {"user_score_chart"}) 
    
    doc_2_list = []
    for link in tag_shows_page:
        # here we are creating the list of all the individual pages of the shows which will come handy in other functions. 
        doc_2_list.append(get_page_content("https://www.themoviedb.org" + link.h2.a['href']))
       # we are going to have the function to return the list of all the information as elements. 
    return tag_title, tag_user_score, doc_2_list


# In[27]:


len(get_show_info(doc))


# In[28]:


doc_2 = get_page_content("https://www.themoviedb.org/movie/436270")


# In[29]:


tag_genre = doc_2.find('span', {"class": "genres"})
tag_genre_list = tag_genre.find_all('a')

check_genre =[]
for tag in tag_genre_list:
    check_genre.append(tag.text)

check_genre


# In[30]:


# lets create a function to get the genres for the movie. 
# i here denotes the element of the list vairable ``doc2_page`` that contains different doc pages. Will come handy later on.
def get_genres(doc2_page, i):
    genres_tags = doc2_page[i].find('span', {"class": "genres"}).find_all('a')
    check_genre =[]
    
    for tag in genres_tags:
        check_genre.append(tag.text)
    return check_genre


# In[31]:


# i here denotes the the element of the list type variable``doc2_page`` that contains different doc pages.

def get_show_Director(doc2_page, i):
    director_tags = doc2_page[i].find_all('li', {'class': 'Director'})
    director_list = []
    
    for t in director_tags:
         director_list.append(t.p.text)
    
    return director_list


# In[32]:


def get_show_cast(doc2_page, i):
    cast_tags = doc2_page[i].find_all('li', {'class': 'card'})
    cast_lis = []
    
    for t in cast_tags:
         cast_lis.append(t.p.text)
    
    return cast_lis


# In[33]:


import pandas as pd

def get_show_details(t_title, t_user_score, docs_2_list):
    # excuting a function here that empties the dictionary every time the function is called.
    scraped_dict =  empty_dict()
    for i in range (0, len(t_title)):
        scraped_dict['Title'].append(t_title[i].h2.text)
        user_score_info(t_user_score, i, scraped_dict)    
        scraped_dict['Release_date'].append(t_title[i].p.text)  
        scraped_dict['Genre'].append(get_genres(docs_2_list, i))        
        scraped_dict['Director'].append(get_show_Director(docs_2_list, i))
        scraped_dict['Cast'].append(get_show_cast(docs_2_list, i))
        
    return pd.DataFrame(scraped_dict)


# In[34]:


tag_title_, tag_user_score_, doc_2_list_ = get_show_info(doc)


# In[35]:


import csv


# In[37]:


x = get_show_details(tag_title_, tag_user_score_, doc_2_list_)
x.to_csv('check.csv')
pd.read_csv('check.csv',index_col=[0])


# In[39]:


import os
base_link = "https://www.themoviedb.org/movie"

# 'i' here means the number of page we want to extract
def create_page_df( i, dataframe_list):
    os.makedirs('shows-data', exist_ok = True)
    next_url = base_link + '?page={}'.format(i)
    doc_top = get_page_content(next_url)
    name_tag, viewer_score_tag, doc_2_lis = get_show_info(doc_top)
    print('scraping page {} :- {}'.format(i, next_url))
    dataframe_data = get_show_details(name_tag, viewer_score_tag, doc_2_lis)
    dataframe_data.to_csv("shows-data/shows-page-{}.csv".format(i) , index = None)
    print(" ---> a CSV file with name shows-page-{}.csv has been created".format(i))
    dataframe_list.append(dataframe_data)


# In[40]:


test_list = []
create_page_df(50 , test_list)


# In[41]:


import pandas as pd
base_link = "https://www.themoviedb.org/movie"

def scrape_top_1000_shows(base_link):
    dataframe_list = []
    # we are going to keep range up to 1001 because we just need up to 1000 movie shows for now. 
    for i in range(1,101):
        create_page_df(i, dataframe_list)
    # here we are using concat function so that we can merge the each dataframe that we got from the each page.    
    total_dataframe = pd.concat(dataframe_list, ignore_index = True)
    
    # with the simple command of to_csv() we can create a csv file of all the pages we extracted.
    csv_complete =  total_dataframe.to_csv('shows-data/Total-dataframe.csv', index= None)
    print(" \n a CSV file named Total-dataframe.csv with all the scraped shows has been created")


# In[42]:


scrape_top_1000_shows(base_link)


# In[43]:


pd.read_csv('shows-data/Total-dataframe.csv')[0:100]


# In[42]:


# Reading the csv file
df_new = pd.read_csv('shows-data/Total-dataframe.csv')
 
# saving xlsx file
GFG = pd.ExcelWriter('Names.xlsx')
df_new.to_excel(GFG, index=False)
 
GFG.save()


# In[43]:


final = pd.ExcelWriter('GFG.xlsx')

