import os
import json
import requests
from time import sleep
from datetime import datetime, timedelta

# Configuration
endpoint_google = "https://serpapi.com/search"
google_params = {"api_key": "97ec6c9e32ddaf413f43a868ffb8e3d2591e4a8b9fea934ac69c191b14f07964",
                 "engine": "google",
                 "num": 100}
endpoint_impaakt = "https://airating.text-analytics.ch/api/v1/jobs"
impaakt_params = {"impaakt_model": True,
                  "entity_model": False,
                  "company_model": False,
                  "topic_model": False}
input_file = "input/20231228_company_topic_queries.csv"
output_dir = "output/2024-01/"

# Create necessary directories
os.makedirs(output_dir + "1_Google", exist_ok=True)
os.makedirs(output_dir + "2_urls", exist_ok=True)
os.makedirs(output_dir + "3_jobs", exist_ok=True)
os.makedirs(output_dir + "4_impaakt", exist_ok=True)
os.makedirs(output_dir + "5_final", exist_ok=True)

# fetch Google SerpAPI
def fetch_google_results():
    with open(input_file, encoding="utf-8") as rfile:
        i = 1
        for line in rfile:
            cols = line.strip().split(",")
            company = cols[0]
            topic = cols[1]
            google_params["q"] = company + " " + topic

            r = requests.get(url=endpoint_google, params=google_params)
            response = r.text
            with open(f"{output_dir}1_Google/{i}.json", "w", encoding="utf-8") as file:
                file.write(response)
            i += 1
            sleep(0.5)

# Extract the URLs from SerpAPI
def extract_urls():
    for file in os.listdir(f"{output_dir}1_Google"):
        with open(f"{output_dir}1_Google/{file}", encoding="utf-8") as rfile:
            data = json.loads(rfile.read())

        sources = []
        with open(f"{output_dir}2_urls/{file}", "w", encoding="utf-8") as wfile:
            for org in data["organic_results"]:
                sources.append(org["link"])
            wfile.write(json.dumps(sources, indent=2))

# Process the URLs with the dedicated webservice
def submit_to_impaakt():
    for file in os.listdir(f"{output_dir}2_urls"):
        with open(f"{output_dir}2_urls/{file}", encoding="utf-8") as rfile:
            data = json.loads(rfile.read())

        sources = [{"url": url} for url in data]
        impaakt_params["source"] = sources

        r = requests.post(url=endpoint_impaakt, json=impaakt_params)
        response = r.text
        with open(f"{output_dir}3_jobs/{file}", "w", encoding="utf-8") as file:
            file.write(response)

# Check for the processing status of all the URLs
def check_impaakt_status():
    for file in os.listdir(f"{output_dir}3_jobs"):
        with open(f"{output_dir}3_jobs/{file}", encoding="utf-8") as rfile:
            data = json.loads(rfile.read())

        job_id = str(data["_id"])
        r = requests.get(f"{endpoint_impaakt}/{job_id}/status")
        status_data = json.loads(r.text)

        if status_data["status"] == "done":
            r = requests.get(f"{endpoint_impaakt}/{job_id}?include_text=true")
            with open(f"{output_dir}4_impaakt/{file}", "w", encoding="utf-8") as file:
                file.write(r.text)
            print(file, "OK")
        else:
            print(file, "KO")

# Prepare the data CSV file for all the queries
def merge_results():
    with open(input_file, encoding="utf-8") as rfile:
        i = 1
        for line in rfile:
            cols = line.strip().split(",")
            company = cols[0]
            topic = cols[1]

            sources = {}
            with open(f"{output_dir}1_Google/{i}.json", encoding="utf-8") as rfile:
                data = json.loads(rfile.read())
                for org in data["organic_results"]:
                    url = org["link"]
                    sources[url] = {
                        "title": org["title"],
                        "organic_position": org["position"],
                        "snippet": org.get("snippet", "")
                    }

            with open(f"{output_dir}4_impaakt/{i}.json", encoding="utf-8") as rfile:
                data = json.loads(rfile.read())
                for org in data["source"]:
                    url = org["url"]
                    sources[url]["impaakt"] = org.get("impaakt", "0")
                    sources[url]["text"] = org.get("text", "")

            with open(f"{output_dir}5_final/{i}.csv", "w", encoding="utf-8") as wfile:
                wfile.write("url\torg_pos\tAIr_pos\tImpaakt_score\ttitle\tsnippet\tprocessed_text\n")
                for url in sources:
                    wfile.write(f"{url}\t{sources[url]['organic_position']}\t.\t{sources[url]['impaakt']}\t{sources[url]['title']}\t{sources[url]['snippet']}\t{sources[url]['text']}\n")

            print(i)
            i += 1

# Main workflow execution
fetch_google_results()
extract_urls()
submit_to_impaakt()
check_impaakt_status()
merge_results()
