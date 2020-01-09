#!/usr/bin/env python
# coding: utf-8

# # Web Scraping with Beautifulsoup library
# This code scraps data from a Wikipedia page and transforms it into a pandas data frame using beautiful-soup library 

# In[1]:


#installing beautifulsoup4
get_ipython().system('pip install beautifulsoup4')
#installing lxml and requests. 
get_ipython().system('pip install lxml')
get_ipython().system('pip install requests')


# In[2]:


#importing libraries
import pandas as pd
from bs4 import BeautifulSoup
import requests
import lxml


# In[3]:


#converting url to a html file 
url= 'https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M'
r = requests.get(url)
Canada_html= r.text


# In[4]:


#Getting the data from the website using beautifulsoup
soup= BeautifulSoup(Canada_html, 'lxml')

#this will print out all html in more readable way 
#print(soup.prettify())


# In order to scrap specific information in a website, we need to know the name of the division.
# To get this information:
# * go to the website
# * right click the thing you want to parse
# * click **Inspect** 
# * A new window is going to be opened and you can see the name of the division
# 
# We are going to scrap the table in the link https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M 

# In[5]:


#This code selects the html docuement belongs to the table
Table = soup.find('table')


# In[6]:


#You can check whether you get the right information or not
#print(Table.prettify())


# In[ ]:


#This code scrap the rows and columns of the data
table_body = Table.find('tbody')
rows = table_body.find_all('tr')
for row in rows:
    cols=row.find_all('td')
    cols=[x.text.strip() for x in cols]
    print(cols)


# In[8]:


#This code saves the output of previous loop to a list
table_body = Table.find('tbody')
rows = table_body.find_all('tr')
lst=[[]]

for row in rows:
    cols=row.find_all('td')
    cols=[x.text.strip() for x in cols]
    lst.append(cols)
    


# In[9]:


#converts list to a data frame
df=pd.DataFrame(lst)
df.head()


# ## Data screening and cleaning in pandas
# We have three goals:
# * Delete cells with a borough that is Not assigned.
# * In one postal code area there may be more than one neighborhood. Combine these on a single row by comma
# * If a cell has a borough but a Not assigned neighborhood, then the neighborhood will be the same as the borough
# 
# As you can see, df has two rows none (Comes from the previous loop) and has no column names, we will start with these.

# In[10]:


#Deleting the first two rows
df.drop([0,1],inplace=True)

#Resetting the index values
df.reset_index(drop=True, inplace=True)
df.head()


# In[11]:


#Give names to columns
df.columns = ['PostalCode', 'Borough','Neigborhood']
df.head()


# In[12]:


#Deleting the cells with a borough that is Not assigned
df=df[df.Borough != 'Not assigned']
df.reset_index(drop=True, inplace=True)
df.head()


# In[14]:


#this code combines Neigborhoods in the same brough by a comma
df2 = df.groupby('Borough').agg({'PostalCode':'first', 
                             'Neigborhood': ', '.join, 
                             }).reset_index()
df2.head()


# In[15]:


#this code resets the column order
df= df2[["PostalCode","Borough","Neigborhood"]]
df.head()


#Combining latitude and longitude data with neighborhood data
#This part includes
#Getting latitude and longitude data
#Combining this data with previous data frame

LLdata=pd.read_csv("https://cocl.us/Geospatial_data")

LLdata.head()
#remaning columns
LLdata.columns= ["PostalCode","Latitude","Longitude"]

#merging the data frames
DfMerged= pd.merge(df,LLdata, on= "PostalCode", how= "left")



