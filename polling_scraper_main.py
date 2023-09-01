
# coding: utf-8

# In[2]:


import pandas as pd
from datetime import datetime
from polling_scraper_functions_v2 import scrape_polling_data, generate_trends_dataframe


# In[3]:


# Define the URL of the polling page
polling_url = "https://cdn-dev.economistdatateam.com/jobs/pds/code-test/index.html"


# In[6]:


if __name__ == "__main__":
    polling_data = scrape_polling_data(polling_url)
    
    polling_data.to_csv('polls.csv')
    
    if polling_data is not None:
        trends_data = generate_trends_dataframe(polling_data)

        if trends_data is not None:
            # Generate CSV files
            trends_data.to_csv('trends.csv')

