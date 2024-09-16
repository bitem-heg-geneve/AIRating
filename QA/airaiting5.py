import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import time
from transformers import pipeline, AutoTokenizer, GPT2LMHeadModel
import re
import spacy
import seaborn as sns
import matplotlib.pyplot as plt
from itertools import zip_longest
import warnings
from collections import OrderedDict
# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Suppress DtypeWarning
warnings.filterwarnings("ignore", category=pd.errors.DtypeWarning)

def read_csv_file(file_path):
    return pd.read_csv(file_path)

def extract_text_from_url(url, timeout=20):
    try:
        response = requests.get(url, timeout=timeout)
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text()
        return text
    except Exception as e:
        print(f"Error occurred while processing URL: {url}")
        print(e)
        return None

def preprocess_text(text):
    if len(text) > nlp.max_length:
        text = text[:nlp.max_length]  # Truncate text to max length
    doc = nlp(text)
    relevant_sentences = [sent.text.strip() for sent in doc.sents if any(ent.label_ for ent in sent.ents)]
    processed_text = " ".join(relevant_sentences)
    return re.sub(r'\n', ' ', processed_text)

def fetch_text_from_urls(urls, timeout=20):
    texts = []
    for url in urls:
        try:
            text = extract_text_from_url(url, timeout=timeout)
            if text:
                processed_text = preprocess_text(text)
                texts.append(processed_text)
        except Exception as e:
            print(f"Error occurred while processing URL: {url}")
            print(e)
    return texts



def generate_question(example_questions, context, tokenizer, model):
    question_generation_pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer)
    generated_question = question_generation_pipeline(f"Generate a question: {context} Answer: {example_questions}", num_return_sequences=1)[0]["generated_text"]
    return generated_question.strip()


def write_questions_to_file(questions, filename):
    with open(filename, 'w') as file:
        for question in questions:
            file.write(question + '\n')

def main():
    start_time = time.time()
    # Read CSV files
    csv_note_source_path = '20230125_tr_note_source.csv'
    csv_datapoints_path = 'datapoints_2024-01-16T15 25 08.159208+01 00.csv'
    df_note_source = read_csv_file(csv_note_source_path)
    df_datapoints = read_csv_file(csv_datapoints_path)

    # Extract URLs and example questions
    urls_source = df_note_source.iloc[1:, 2]
    example_questions = list(["What is the impact of the company on " + point + " ?" for point in df_datapoints.iloc[:, 6]])
    example_questions = set(example_questions)

    # Fetch text from URLs
    texts = fetch_text_from_urls(urls_source.iloc[66:70])

    # Initialize tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained("EleutherAI/gpt-neo-125M")
    model = GPT2LMHeadModel.from_pretrained("EleutherAI/gpt-neo-125M", ignore_mismatched_sizes=True)

    # Generate questions
    generated_questions = []
    for i, context in enumerate(texts):
        generated_question = generate_question(example_questions, context, tokenizer, model)
        generated_questions.append(generated_question)
        print(f"Processed {i + 1}/{len(texts)}")
    
    # Write questions to file
    write_questions_to_file(generated_questions, 'generated_questions2.txt')



    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time} seconds")

if __name__ == "__main__":
    main()

"""
questions_topics_dict = {}

    for question, topic in zip(example_questions, df_datapoints.iloc[:, 5]):
        if topic not in questions_topics_dict:
            questions_topics_dict[topic] = []
        questions_topics_dict[topic].append(question)

    # Sort the dictionary by topics
    questions_topics_dict = OrderedDict(sorted(questions_topics_dict.items()))


    # Extract just the questions
    topics = list(questions_topics_dict.keys())
    print(topics)

    # Extract just the topics
    questions = list(questions_topics_dict.values())
    #print(questions)
    print("There are " + str(len(example_questions)) + " different example questions.")





0, 1, 2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,18,19,20,21,23,24,25,26,27,28,29,30,
31,32,33,34,35,36,37,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,

"""