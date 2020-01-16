#!/usr/bin/env python
# coding: utf-8

# # IBM DATA SCIENCE SPECIALIZATION CAPSTONE PROJECT
# ## OPTIMAL PLACES TO LIVE
# # Purpose of the project
# 
# The purpose of this project is to make suggestions about the places people may like to live. Moreover, They will have information about the rental prices of the possible lovable cities and the minimum cost of a place with certain attributes. 
# 
# **Business case** : When people choose the place they would like to live, they consider many attributes. web sites or applications used for real estate generally provides some information about neighborhood like nearby schools and amenities. In this project, I aim to enhance customer experience by including social environment of cities and providing a wider range of possibilities. By using this information, a real estate consultant may give additional advices and information to her customers.
# 
# **Audience:** In this project I am going to suggest alternative places to live to a person who likes to live in Natick, MA. For this specific purpose, my audience is people who like to live in Natick, MA and looking to find an apartment in a place they will like to live. The location can be manipulated easily and we can use this project for any location.

# # Description of Data
# In this project I am going to use three data sources
# **Foursquare data:** This will provide us the venue information for the cities in MA. I am going to use this data to cluster the cities and find the similar cities.
# **Zillow data:** This will provide us rent estimates of cities in MA. Zillow provides different types of data. I am going to use zillow rent index for multifamily condos and apartments. 
# You can download data from this link https://www.zillow.com/research/data/ . In this link you will find four sections to get the data. I used the rental sections as I need the rent information. As data type I selected the first one (ZRI summary: multifamiliy, sfr condo) and as geography I selected zipcode.
# 
# Zillow provides rent index for each city in a state. This data set have 12 columns which are date, region name (zip code),state, metro area name, county, city, size rank, zillow rent index, and the remaining are weights for different types of housing. I am going to use zip code, city and rent index columns. You can find additional information about how zillow rent indexes are calculated from this link. https://www.zillow.com/research/methodology-zillow-rent-index-2019-25172/
# 
# **US Zip Code Latitude and Longitude data:** You can access latitude and longitude data from this link. https://public.opendatasoft.com/explore/dataset/us-zip-code-latitude-and-longitude/export/?q=MA&refine.state=MA 
# 

# In[5]:


#Importing pandas
import pandas as pd


# In[6]:


#Zillow rent data is going to look like something like this.
Zdata= pd.read_csv("Zip_Zri_AllHomesPlusMultifamily_Summary.csv", encoding = "ISO-8859-1")
Zdata.head()
#Note I received an error while reading csv file as this file is not encoded 'utf-8' and I solved this problem using encoding = "ISO-8859-1" command in read_csv function


# In[7]:


# US zip code latitude and longtidu data
LLdata= pd.read_csv("us-zip-code-latitude-and-longitude.csv", sep=";")
LLdata.head()
#This data is semi column seperated. To read this data properly we need to use sep=";" argument in read_csv function


# ## Data Analysis
# As explained in previous section, foursquare,US latitude and longitude data and zillow data are used in this project. Data analysis was conducted in five steps
# 1. Gathering data for MA
# 2. Import foursquare venues data from foursquare API
# 3. Cluster cities according to their venues using K means clustering algorithm
# 4. Merge clustered data with zillow rent index data
# 5. Select Natic's cluster and order this cluster according to rent estimate
# 

# ### 1. Gathering data for MA

# In[8]:


#Rent data for MA
RentMA= Zdata.loc[Zdata["State"]=="MA",["RegionName","City","Zri"]]
RentMA.head()


# In[9]:


#Location data for MA
LOC_MA= LLdata.loc[LLdata["State"]=="MA",["Zip","City","Latitude","Longitude"]]
LOC_MA.head()


# In[10]:


# Lets check the dimension of each data frame
print(" Dimension of rent data is",RentMA.shape, "\n","Dimension of location data is", LOC_MA.shape)


# In[28]:


#The number of rows are different. This means some rent data is missing in zillow data. 
#We are going to use "NA" for missing data in the further analysis


# ### 2. Import foursquare venues data from foursquare API

# In[11]:


import requests # library to handle requests
import random 


# In[12]:


#Foursquare credentials
LIMIT = 50
radius = 500
CLIENT_ID = 'SLSX3CCXO3X2E0AGUV54D1BSSPNBCIFZD4RUCOGK53QZWVFL' # your Foursquare ID
CLIENT_SECRET = 'CHBJYULAVFGWPV2MJLTC44D5GO0TFLF3RYN5HZ034QYTMWZY' # your Foursquare Secret
VERSION = '20180605' # Foursquare API version


# In[13]:


#function that gets the nearby venues
#This function is written by course instructers. 
def getNearbyVenues(names, latitudes, longitudes, radius=500):
    
    venues_list=[]
    for name, lat, lng in zip(names, latitudes, longitudes):
        print(name)
            
        # create the API request URL
        url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
            CLIENT_ID, 
            CLIENT_SECRET, 
            VERSION, 
            lat, 
            lng, 
            radius, 
            LIMIT)
            
        # make the GET request
        results = requests.get(url).json()["response"]['groups'][0]['items']
        
        # return only relevant information for each nearby venue
        venues_list.append([(
            name, 
            lat, 
            lng, 
            v['venue']['name'], 
            v['venue']['location']['lat'], 
            v['venue']['location']['lng'],  
            v['venue']['categories'][0]['name']) for v in results])

    nearby_venues = pd.DataFrame([item for venue_list in venues_list for item in venue_list])
    nearby_venues.columns = ['Neighborhood', 
                  'Neighborhood Latitude', 
                  'Neighborhood Longitude', 
                  'Venue', 
                  'Venue Latitude', 
                  'Venue Longitude', 
                  'Venue Category']
    
    return(nearby_venues)


# In[14]:


#Selecting venues in MA
MA_venues = getNearbyVenues(names=LOC_MA['City'],
                                   latitudes=LOC_MA['Latitude'],
                                   longitudes=LOC_MA['Longitude']
                                  )
#As we have 766 cities and we requested 50 venue for each city, this may take some time


# In[ ]:


MA_venues.head()


# ### 3. Cluster cities according to their venues using KNN algorithm

# In[ ]:


# import k-means from clustering stage
from sklearn.cluster import KMeans


# In[ ]:


# creating dummy variables for each venue category

# one hot encoding
MA_onehot = pd.get_dummies(MA_venues[['Venue Category']], prefix="", prefix_sep="")

# add neighborhood column back to dataframe

MA_onehot['City'] = LOC_MA['City'] 

# move CİTY column to the first column
fixed_columns = [MA_onehot.columns[-1]] + list(MA_onehot.columns[:-1])
MA_onehot = MA_onehot[fixed_columns]

MA_onehot.head()


# In[ ]:


MA_grouped = MA_onehot.groupby('City').mean().reset_index()
MA_grouped.head()


# In[ ]:


MA_grouped_Cluster=MA_grouped.drop('City', 1)


# In[ ]:


import numpy as np 
import matplotlib.pyplot as plt 
get_ipython().run_line_magic('matplotlib', 'inline')


# In[ ]:


#Deciding optimal number of clusters
Sum_of_squared_distances = []
K = range(2,15)
for k in K:
    km = KMeans(n_clusters=k)
    km = km.fit(MA_grouped_Cluster)
    Sum_of_squared_distances.append(km.inertia_)


# In[ ]:


#Plotting Sum of square distances
plt.plot(K, Sum_of_squared_distances, 'bx-')
plt.xlabel('k')
plt.ylabel('Sum_of_squared_distances')
plt.title('Elbow Method For Optimal k')
plt.show()


# In[ ]:


#Clustering neigborhoods with optimum number of clusters
k_means = KMeans(init="k-means++", n_clusters=4, n_init=12)
k_means.fit(MA_grouped_Cluster)
k_means.labels_[0:10]


# In[ ]:


# add clustering labels
MA_grouped.insert(0, 'Cluster Labels', kmeans.labels_)


# ### 4. Merge clustered data with zillow rent index data

# In[ ]:


#merging data
MA_merged=LOC_MA.join(MA_grouped.set_index('City'), on='City')
MA_final=MA_merged.join(RentMA..set_index('City'), on='City',how= "left")
MA_final.head()


# ### 5. Select Natik's cluster and order this cluster according to rent estimate

# In[ ]:


#Find Natik's cluster
Natik_cluster= MA_final.loc[MA_final["City"=="Natik"],"Cluster Labels"]
Natik_cluster


# In[ ]:


#Select this cluster
ClusterK=MA_final.loc[MA_final["Cluster Labels"]==Natik_cluster]
ClusterK.head()


# In[ ]:


#Ordering data
ClusterK.sort_values(by=['Zri'])


# In[ ]:





# ## Results
# The results of the study indicated that there are ---- cities in MA who has similar social environment with Natik. From these cities Natic is the---- most expensive city. The cheapest city in this category is -----. So we can recommend our customer to look for these cities.

# In[ ]:




