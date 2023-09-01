import pandas as pd
from datetime import datetime
from polling_scraper_functions import scrape_polling_data, generate_trends_dataframe

# Define the URL of the polling page
POLLING_URL = "https://cdn-dev.economistdatateam.com/jobs/pds/code-test/index.html"

def main():
    polling_data = scrape_polling_data(POLLING_URL)
    
    polling_data.to_csv('polls.csv')
    
    if polling_data is not None:
        trends_data = generate_trends_dataframe(polling_data)

        if trends_data is not None:
            # Generate CSV files
            trends_data.to_csv('trends.csv')

if __name__ == "__main__":
    main()
