import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import time
from transformers import pipeline
from transformers import AutoTokenizer
import re
import spacy
import seaborn as sns
import matplotlib.pyplot as plt
from itertools import zip_longest

start_time = time.time()

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Replace 'your_file.csv' with the actual path to your CSV file
csv_note_path = '20230125_tr_note.csv'
csv_note_source_path = '20230125_tr_note_source.csv'
csv_topic_path = '20230125_tr_topic.csv'
csv_topic_category_path = '20230125_tr_topic_category.csv'
csv_datapoints_path = 'datapoints_2024-01-16T15 25 08.159208+01 00.csv'

# Read the CSV file into a pandas DataFrame
df_note = pd.read_csv(csv_note_path)
df_topic = pd.read_csv(csv_topic_path)
df_note_source = pd.read_csv(csv_note_source_path)
df_topic_category = pd.read_csv(csv_topic_category_path)
df_datapoints = pd.read_csv(csv_datapoints_path)

column_types = {'7': str}

df_note = pd.read_csv(csv_note_path, low_memory=False)
df_note_source = pd.read_csv(csv_note_source_path, dtype=column_types, low_memory=False)
#df_datapoints = pd.read_csv(csv_datapoints_path, dtype=column_types, low_memory=False)

datapoints = df_datapoints.iloc[:,6]
urls_source = df_note_source.iloc[1:,2]

example_questions = []
for point in datapoints:
    example_questions.append("What is the impact of the company on " + point + " ?")

example_questions = list(set(example_questions))
print("There are " + str(len(example_questions)) + " different example questions.")
#===================================== FUNCTIONS
# Function to extract text from a URL
def extract_text_from_url(url):
    try:
        # Fetch HTML content from the URL
        response = requests.get(url)
        # Parse HTML using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        # Extract text from HTML
        text = soup.get_text()
        return text
    except Exception as e:
        print(f"Error occurred while processing URL: {url}")
        print(e)
        return None


def preprocess_text(text):
    # Process the text with spaCy
    doc = nlp(text)

    # Extract sentences that contain named entities
    relevant_sentences = [sent.text.strip() for sent in doc.sents if any(ent.label_ for ent in sent.ents)]

    # Join the relevant sentences to get the final processed text
    processed_text = " ".join(relevant_sentences)

    text_without_newlines = re.sub(r'\n', ' ', processed_text)

    return text_without_newlines

#======================== END FUNCTIONS

firsturl = urls_source.iloc[:2]
first_h = urls_source.iloc[[0, 1, 2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,18,19,21,23,24,25,26,27,28]]#,30,31,32,33,34,35,36,37,38,39,40]]

# Extract text from each URL in the 'url' column
text_from_urls = []
time_limit = 20
start_time_loop = time.time()
j=0
for url in first_h:
    start_time_loop = time.time()
    text = extract_text_from_url(url)
    j=j+1
    print(j)
    end_time_loop = time.time()
    elapsed_time = end_time_loop - start_time_loop
    if elapsed_time > 20:
        print(f"Skipping iteration due to timeout ({elapsed_time} seconds)")
        continue
    if text:
        processed_text = preprocess_text(text)
        text_from_urls.append(processed_text)

# 'text_from_urls' will contain the extracted text from each URL
#print(text_from_urls[0])



#===================================QA
answers = []
scores = []
generated_questions = []

i=0

for context in text_from_urls:
    # Load the pre-trained BERT QA model
    qa_pipeline = pipeline("question-answering", model="deepset/bert-large-uncased-whole-word-masking-squad2")

    # Load the question generation pipeline
    question_generation_pipeline = pipeline("text2text-generation", model="valhalla/t5-small-qg-prepend")

    # Choose the model (you can replace 'bert-base-uncased' with the desired model)
    model_name = 'bert-base-uncased'

    # Load the tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # Tokenize the text
    tokens = tokenizer.tokenize(tokenizer.decode(tokenizer.encode(context)))

    # Get the number of tokens
    num_tokens = len(tokens)

    # Print the result
    print("Number of tokens for the context is:", num_tokens)


    # Generate questions in the style of provided examples for the given context
    generated_questions = []
    for example_question in example_questions:
        input_text = f"Generate a question: {context} Answer: {example_question}"
        generated_question = \
        question_generation_pipeline(input_text, max_length=50, num_beams=5, length_penalty=0.6)[0]["generated_text"]
        generated_questions.append(generated_question.strip())

    # Ask a question
    print("The generated question is : ", generated_question)

    #context = context[:600]

    # Perform question-answering
    answer = qa_pipeline(question=generated_question, context=context)
    answers.append(answer['answer'])
    scores.append(answer['score'])

    # Print the answer
    print(answer)

    i=i+1
    print(i)




#==================================== PLOTING

# Define the bins
bins = [0, 0.4, 0.6, 0.8, 0.9, 1]

# Create a histogram
hist, edges = np.histogram(scores, bins=bins)

# Plot the histogram
plt.bar(range(len(hist)), hist, align='center', color='blue', alpha=0.7)
plt.show()


# Set labels and title
plt.xlabel('Score Ranges')
plt.ylabel('Frequency')
plt.title('Distribution of Scores')

# Set x-axis ticks and labels
plt.xticks(range(len(bins) - 1), [f'[{bins[i]};{bins[i + 1]}]' for i in range(len(bins) - 1)])

# Display the plot
plt.show()
print(np.histogram(scores, bins=bins))


end_time = time.time()
elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time} seconds")

"""




"""