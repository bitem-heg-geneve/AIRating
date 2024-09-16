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
import warnings
# Load spaCy model
nlp = spacy.load("en_core_web_sm")
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from transformers import BertForMaskedLM, BertTokenizer
import torch


start_time = time.time()

def read_questions_from_file(filename):
    with open(filename, 'r') as file:
        questions = [line.strip() for line in file.readlines()]
    return questions

def write_questions_to_file(questions, filename):
    with open(filename, 'w') as file:
        for question in questions:
            file.write(question + '\n')

generated_questions = read_questions_from_file('generated_questions.txt')

# Load pre-trained T5 model and tokenizer
model_name = "bert-base-uncased"
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertForMaskedLM.from_pretrained(model_name)


# Function to rephrase a question
def rephrase_questions(questions):
    rephrased_questions = []
    for question in questions:
        # Tokenize the question
        try:
            tokenized_question = tokenizer.encode(question, add_special_tokens=False, return_tensors="pt")
        except Exception as e:
            print(f"Error tokenizing question: {question}")
            print(e)
            continue

        # Ensure the tokenized question is not empty
        if tokenized_question.numel() == 0:
            print(f"Failed to tokenize question: {question}")
            continue

        # Get masked token index
        masked_indices = torch.where(tokenized_question == tokenizer.mask_token_id)[1]

        # Check if there are any masked tokens
        if len(masked_indices) == 0:
            print(f"No masked token found in question: {question}")
            continue

        # Take the first masked token index
        masked_index = masked_indices[0].item()

        # Generate rephrased question by predicting masked token
        with torch.no_grad():
            outputs = model(tokenized_question)
            predictions = outputs[0][0, masked_index].topk(5)  # Get top 5 predictions
            rephrased_question = []
            for token_id in predictions.indices:
                token = tokenizer.decode([token_id.item()])
                rephrased_question.append(token)
            rephrased_questions.append(' '.join(rephrased_question))

    return rephrased_questions


# Rephrase questions
rephrased_questions = rephrase_questions(generated_questions)

# Output rephrased questions
for original, rephrased in zip(generated_questions, rephrased_questions):
    print(f"Original Question: {original}")
    print(f"Rephrased Question: {rephrased}\n")


write_questions_to_file(rephrased_questions, 'rephrased_questions.txt')

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time} seconds")