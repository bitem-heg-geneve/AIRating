
# Annotator API

## Overview

The Annotator API is a tool designed to scrape web sources, including HTML pages and PDFs, extract text, and annotate the content for Impaakt rating, SASB topics, and company mentions.

## Deployment Steps

To deploy the Annotator API, follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/bitem-heg-geneve/AIRating.git
   cd AIRating/annotator
   ```

2. **Set Execution Permissions**:
   ```bash
   chmod 777 ./backend/app/run.sh
   ```

3. **Build and Start the Docker Containers**:
   Ensure you are in the root directory of the repository, then run:
   ```bash
   docker compose -f "docker-compose.dev.yml" up --build -d
   ```

4. **Unpack Resources**:
   The `resources` subfolder contains zipped files that must be unpacked before running the API. Unpack the following files:
   
   - `topics.zip`
   - `company.zip`
   - `impaakt.zip`

   Ensure that these files are correctly extracted to the appropriate directories.

## Configuration

The configuration for the Annotator API, including setting up multiple workers and enabling GPU support, can be done in the compose.dev.yml file. 
Below is an example of how the services are configured:
```yaml
version: '3.9'

services:
  mongodb:
    extends:
      file: common-services.yml
      service: mongodb
    deploy:
      resources:
        reservations:
          cpus: '0.1'
          memory: '3g'
  
  redis:
    extends:
      file: common-services.yml
      service: redis
  
  flower:
    extends:
      file: common-services.yml
      service: flower
  
  api:
    extends:
      file: common-services.yml
      service: worker
    ports:
      - "8001:8001"
      - "5678:5678" # debug
    env_file:
      - ./images/env
    command: python -m debugpy --listen 0.0.0.0:5678 -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
    tty: true

  ingress: # ingress worker
    extends:
      file: common-services.yml
      service: worker
    ports:
      - "5671:5671" # debug
    env_file:
      - ./images/env
    command: watchmedo auto-restart -d "/app" --recursive -p '*.py' -- python -m debugpy --listen 0.0.0.0:5671 -m celery -A app.main.celery worker --loglevel=info -Q default,ingress --hostname=ingress@%h --concurrency=10
  
  infer: # inference worker
    extends:
      file: common-services.yml
      service: worker
    ports:
      - "5672:5672" # debug
    env_file:
      - ./images/env
    command: watchmedo auto-restart -d "/app" --recursive -p '*.py' -- python -m debugpy --listen 0.0.0.0:5672 -m celery -A app.main.celery worker --loglevel=info -Q infer --hostname=infer@%h --pool=solo
    deploy:
      replicas: 1
```


## Usage

Once the deployed, the Annotator API will be available for use. 
You can access the API documentation and explore its endpoints using the following links:

- **API Documentation**: [http://localhost:8001/docs](http://localhost:8001/docs)
- **Flower Monitoring Tool**: [http://localhost:5555](http://localhost:5555)

### Creating an Annotator Job

The Annotator API allows you to create jobs that include a list of candidate sources. Here's how the job processing works:

- **Source URL**: Each source in the job must include a URL.
- **Text Inclusion**: Optionally, you can include text for each source. If no text is provided, the system will attempt to scrape the URL and extract text from either HTML or PDF documents.
- **Impaakt Rating**: The system will process the Impaakt rating by default, but it is optional. Only sources with text will be processed.
- **SASB Topic Annotation**: SASB topic annotation is enabled by default but can be customized. For each source, you can include a predefined list of topics in the request. If no list is provided, the system will attempt to annotate topics from the text. Only sources with text will be processed.
- **Company Mentions**: This step is also enabled by default but is optional. Only sources that have been annotated with entities will be processed for company mentions.
