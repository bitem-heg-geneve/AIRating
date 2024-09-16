import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import time
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import re
import spacy
import seaborn as sns
import matplotlib.pyplot as plt
from itertools import zip_longest
import warnings
from huggingface_hub import login


access_token = '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'
login(access_token)


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

def answer_questions(question, context):
    model_name = "meta-llama/Llama-2-7b-chat-hf"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name, use_auth_token=True)

    input_text = f"Context: {context}\nQuestion: {question}\nAnswer:"
    inputs = tokenizer(input_text, return_tensors="pt", truncation=True, max_length=2048)
    outputs = model.generate(inputs['input_ids'], max_new_tokens=150)
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return answer

def write_questions_to_file(questions, answers, filename):
    with open(filename, 'w') as file:
        for question, ans, score in zip(questions, answers, scores):
            file.write(question + ' -> answer : ' + ans + '\n')

def read_questions_from_file(filename):
    with open(filename, 'r') as file:
        questions = [line.strip() for line in file.readlines()]
    return questions

def main():
    start_time = time.time()
    # Read CSV files
    csv_note_source_path = '20230125_tr_note_source.csv'
    df_note_source = read_csv_file(csv_note_source_path)

    # Extract URLs
    urls_source = df_note_source.iloc[1:, 2]
    # Fetch text from URLs
    texts = fetch_text_from_urls(urls_source.iloc[[0, 1, 2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20, 21, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65]])
    print(len(texts))
    
    # Read questions from file
    generated_questions = read_questions_from_file('generated_questions.txt')

    # Generate answers
    answers= []
    for i, (context, question) in enumerate(zip(texts, generated_questions)):
        if context.strip():
            ans = answer_questions(question, context)
            answers.append(ans)
            print(f"Processed {i + 1}/{len(texts)}")
        else:
            print(f"Skipped question {i + 1} because context is empty")
            answers.append(f"Skipped question {i + 1} because context is empty")
            

     # Write answers to file
    write_questions_to_file(generated_questions, answers, 'generated_answers_Llama_2_7b_chat_hf.txt')


    # Make it an excel
    excel = {'Questions': generated_questions,
             'Answers': answers,
             }

    df_excel = pd.DataFrame(excel)
    df_excel.to_excel('AiQa_results.xlsx', index=False)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time} seconds")

if __name__ == "__main__":
    main()
