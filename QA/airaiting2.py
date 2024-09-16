import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from transformers import pipeline
from transformers import AutoTokenizer
import re
import spacy
import seaborn as sns

import matplotlib.pyplot as plt
import requests




url = 'https://airating.text-analytics.ch/api/v1/jobs'
headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json',
}

data = {
    "text_token_min": 50,
    "text_token_max": 600,
    "impaakt_model": True,
    "entity_model": False,
    "company_model": False,
    "topic_model": False,
    "source": [
        {"url": "https://www.occ.gov/news-issuances/news-releases/2011/nr-occ-2011-47c.pdf"},
        {"url": "https://www.pionline.com/esg/dws-sell-excessive-greenwashing-doubt-citi-analysts-say"},
        # ... (add more URLs)
    ]
}

response = requests.post(url, json=data, headers=headers)

# Check the response
if response.status_code == 200:
    response_json = response.json()

    # Check if the key "extracted_text" exists in the response
    if "extracted_text" in response_json:
        extracted_text = response_json["extracted_text"]
        print("Extracted Text:")
        print(extracted_text)
    else:
        print("Extracted text not found in the response.")
else:
    print(f"Request failed with status code {response.status_code}")
    print(response.text)






"""

#import mysql.connector

scores = [0.2, 0.5, 0.8, 0.3, 0.9]

# Create a bar plot using Matplotlib
plt.bar(range(len(scores)), scores, color='blue')

# Set labels and title
plt.xlabel('Data Points')
plt.ylabel('Scores')
plt.title('Scores between 0 and 1')

# Display the plot
plt.show()






# Establish a connection to the database
conn = mysql.connector.connect(
    host='localhost',  # Or use the actual host name if different
    user='esteban',  # Replace with your MySQL username
    password='ClouksiBella,5',  # Replace with your MySQL password
    database='impaakt_db_prod'  # Replace with the name of your database
)

# Check if the connection is successful
if conn.is_connected():
    print("Connected to the MySQL database")

# Perform database operations here

# Close the connection when done
conn.close()



"""