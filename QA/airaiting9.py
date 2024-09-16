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





"""
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