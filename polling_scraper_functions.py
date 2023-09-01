
# coding: utf-8

# In[1]:


import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging


# In[2]:


# Define email settings for error notifications
SMTP_SERVER = "your-smtp-server.com"
SMTP_PORT = 587
SMTP_USERNAME = "your-username"
SMTP_PASSWORD = "your-password"
EMAIL_FROM = "your-email@example.com"
EMAIL_TO = "your-email@example.com"


# In[3]:


# Configure logging
logging.basicConfig(filename="polling_scraper.log", level=logging.ERROR)


# In[5]:


# Function to send email notifications for errors
def send_error_email(subject, message):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        server.quit()
    except Exception as e:
        logging.error(f"Failed to send error email: {str(e)}")


# In[2]:


# Function to scrape polling data from the webpage
def scrape_polling_data(url):
    '''
    takes a URL for polling data, scrapes the table and generates the data frame needed
    '''
    try:
        # Use requests to fetch the HTML content of the webpage
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors

        soup = BeautifulSoup(response.text, "html.parser")

        # Find the table containing polling data
        table = soup.find('table')

        # Initialize lists to store data
        dates = []
        pollsters = []
        sample_sizes = []
        candidate_data = []

        # Extract column headers from the thead section
        headers = table.find('thead').find_all('th')
        candidate_names = [header.get_text().strip() for header in headers[3:]]

        # Extract data from the table (excluding thead)
        for row in table.find_all('tr')[1:]:
            columns = row.find_all('td')

            date = columns[0].get_text().strip()
            pollster = columns[1].get_text().strip()
            sample_size = columns[2].get_text().strip()

            # Extract candidate data as a list
            candidate_values = [col.get_text().strip() for col in columns[3:]]

            # Append data to lists
            dates.append(date)
            pollsters.append(pollster)
            sample_sizes.append(sample_size)
            candidate_data.append(candidate_values)

        # Create DataFrames for candidates and main data
        candidate_df = pd.DataFrame(candidate_data, columns=candidate_names)
        main_df = pd.DataFrame({
            "Date": dates,
            "Pollster": pollsters,
            "Sample Size": sample_sizes
        })

        # Concatenate the candidate DataFrame and main DataFrame
        df = pd.concat([main_df, candidate_df], axis=1)
        df["Sample Size"]=df["Sample Size"].str.replace(',', '')
        df["Sample Size"] =df["Sample Size"].str.replace('[^\w\s]', '')
        df["Sample Size"].astype(float)
        
        for col in df[list(df.columns[3:])].columns:
            #print(col)
            df[col]=df[col].astype(str).str.replace("%", "")
            df[col] =df[col].str.replace('[^\w\.]', '')
            df[col] = pd.to_numeric(df[col] , errors='coerce')
            df[col] =df[col] /100

    
        
        return df

    except Exception as e:
        logging.error(f"Error while scraping polling data: {str(e)}")
        send_error_email("Polling Data Scraper Error", str(e))
        return None


# In[6]:


# Function to calculate the 7-day rolling average
def calculate_rolling_average(data, window=7):
    return data.rolling(window=window).mean()

# Function to generate the trends dataframe
def generate_trends_dataframe(poll_data):
    '''
    
    input is the polling data frame scraped from the URL
    generates a rolling average for the candidates 
    '''
    df=poll_data.copy()
    df['date_dt'] = pd.to_datetime(df['Date'])
    
    # Set the 'Date' column as the index
    df.set_index('date_dt', inplace=True)
    
    # Define the start date (October 11th, 2023)
    start_date = df.index.min()
    
    # Generate a date range from start_date to the last date in the poll data
    end_date = df.index.max()
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Create an empty DataFrame to store the trends
    trends_df = pd.DataFrame(index=df.index)
    
    # Calculate the rolling average for each candidate
    candidates = df[df.columns[3:]].columns
    for candidate in candidates:
        trends_df[f'{candidate}'] = calculate_rolling_average(df[candidate])
    
    trends_df.reset_index(inplace=True)
    return trends_df


# In[8]:


# Function to generate CSV files
def generate_csv_file(df):
    try:
        df.to_csv(f"{df}.csv", index=False)
    except Exception as e:
        logging.error(f"Error while generating CSV files: {str(e)}")
        send_error_email("CSV Generation Error", str(e))

