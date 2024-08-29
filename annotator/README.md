# Impaakt API

## Deployment steps:
- clone repository
- chmod 777 ./backend/app/run.sh
<!-- - unzip ./resources/impaakt.zip -->
- docker compose -f "docker-compose.dev.yml" up --build -d

## Usage
[http://localhost:8001/docs](http://localhost:8001/docs)

Create an Impaakt job including a list of candicate sources:
- Each source must include an url
- For each source a text can optionally be included in the request. For sources for which no text is provided, the system will attempt to crawl the url and extract text from either html or PDF documents.
- Impaakt ranking is default but optional. Only sources with text will be processed.
- Named entity recognition (NER) is default but optional. For each source a NER-list can be included in the request. For sources for which no NER-list is provided the system will attempt to extract entities. Only sources with text will be processed.
- Company classification is default but optional. Only sources with a NER-list will be processed.
