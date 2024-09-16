import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import time
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForCausalLM
import re
import spacy
import seaborn as sns
import matplotlib.pyplot as plt
from itertools import zip_longest
import os
import warnings
# Load spaCy model
nlp = spacy.load("en_core_web_sm")
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from huggingface_hub import login

start_time = time.time()

# Use your Hugging Face access token
access_token = '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'
login(access_token)

# Set your Hugging Face API token
#os.environ["HF_HOME"] = "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"



def read_questions_from_file(filename):
    with open(filename, 'r') as file:
        questions = [line.strip() for line in file.readlines()]
    return questions

def write_questions_to_file(questions, filename):
    with open(filename, 'w') as file:
        for question in questions:
            file.write(question + '\n')

generated_questions = read_questions_from_file('generated_questions.txt')

# Load pre-trained GPT-2 model and tokenizer
# Set your Hugging Face API token
#set_hf_token("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")
model_name = "meta-llama/Meta-Llama-3-8B"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Define text generation function
def generate_rephrased_question(question):
    inputs = tokenizer.encode("Question: " + question, return_tensors="pt", max_length=50, truncation=True)
    outputs = model.generate(inputs, max_length=100, num_return_sequences=1, temperature=0.8, pad_token_id=tokenizer.eos_token_id, do_sample=True)
    rephrased_question = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return rephrased_question

# Rephrase questions
rephrased_questions = [generate_rephrased_question(question) for question in generated_questions]

# Output rephrased questions
for original, rephrased in zip(generated_questions, rephrased_questions):
    print(f"Original Question: {original}")
    print(f"Rephrased Question: {rephrased}\n")


write_questions_to_file(rephrased_questions, 'rephrased_questions.txt')

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time} seconds")