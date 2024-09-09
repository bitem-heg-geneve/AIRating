import asyncio
import io
import logging
import os
import random
import re
import time
from collections import ChainMap
from random import shuffle

import fitz
import httpx
from app.models.job import Job
from app.models.source import Source
from asgiref.sync import async_to_sync
from bs4 import BeautifulSoup
from bs4.element import Comment
from celery import shared_task
from playwright.async_api import Playwright, async_playwright
from playwright_stealth import stealth_async

TEXT_CRAWL_CONCURRENCY = int(os.environ["TEXT_CRAWL_CONCURRENCY"])
TEXT_TOKEN_MIN = int(os.environ["TEXT_TOKEN_MIN"])
TEXT_TOKEN_MAX = int(os.environ["TEXT_TOKEN_MAX"])
PDF_PAGES_MAX = int(os.environ["PDF_PAGES_MAX"])
URL_REGEX = re.compile(r"""(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))""")
MULTIPLE_PERIODS_REGEX = re.compile(r'\.{2,}')
WHITESPACE_REGEX = re.compile(r"(\s\s+|\t+|\n+)")

def clean_text(text):
    """
    Cleans the given text by removing URLs, multiple periods, and extra whitespace.

    Args:
        text (str): The text to be cleaned.

    Returns:
        str: The cleaned text.
    """
    text = URL_REGEX.sub(" ", text)
    text = MULTIPLE_PERIODS_REGEX.sub(".", text)
    text = WHITESPACE_REGEX.sub(" ", text).strip()

    return text


# def clean_text(text):
#     text = re.sub(
#         r"""(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))""",
#         " ",
#         text,
#     )
#     text = re.sub(r'\.{2,}', '.', text)
#     text = re.sub(r"(\s\s+|\t+|\n+)", " ", text).strip()

#     return text


# def tag_visible(element):
#     if element.parent.name in [
#         "style",
#         "script",
#         "head",
#         "title",
#         "meta",
#         "[document]",
#     ]:
#         return False
#     if isinstance(element, Comment):
#         return False
#     return True

def tag_visible(element):
    """
    Determines if an HTML element is visible or not.

    Args:
        element (BeautifulSoup.Tag): The HTML element to check.

    Returns:
        bool: True if the element is visible, False otherwise.
    """
    invisible_tags = {
        "style",
        "script",
        "head",
        "title",
        "meta",
        "[document]",
    }

    return not (element.parent.name in invisible_tags or isinstance(element, Comment))


# def html2text(html):
#     soup = BeautifulSoup(html, "html.parser")
#     texts = []

#     # page title
#     if soup.title is not None:
#         texts.append(soup.title.string)

#     # # paragraphs
#     # paragraphs = soup.find_all("p")
#     # for p in paragraphs:
#     #     if p:
#     #         text = clean_text(p.get_text())
#     #         if len((text).split()) > 20:
#     #             texts.append(text)

#     visible_texts = soup.findAll(text=True)
#     for t in filter(tag_visible, visible_texts):
#         t = clean_text(t.strip())
#         if len((t).split()) > 10:
#             texts.append(t)

#     # youtube texts
#     yt_desc = []
#     yt_desc.extend(
#         [
#             description
#             for description in soup.find_all(
#                 "span",
#                 {
#                     "class": "yt-core-attributed-string yt-core-attributed-string--white-space-pre-wrap"
#                 },
#             )
#         ]
#     )
#     if yt_desc:
#         text = clean_text(yt_desc[-1].get_text())
#         texts.append(text)

#     yt_comments = []
#     yt_comments.extend(
#         [
#             comment
#             for comment in soup.find_all(
#                 "yt-formatted-string", {"class": "style-scope ytd-comment-renderer"}
#             )
#         ]
#     )
#     for c in yt_comments:
#         if c:
#             text = clean_text(c.get_text())
#             texts.append(text)

#     return " ".join(texts)

def html2text(html):
    """
    Convert HTML content to plain text.

    Args:
        html (str): The HTML content to be converted.

    Returns:
        str: The plain text extracted from the HTML content.
    """
    soup = BeautifulSoup(html, "html.parser")
    texts = []

    # page title
    if soup.title is not None:
        texts.append(soup.title.string)

    # visible texts
    visible_texts = [clean_text(t.strip()) for t in filter(tag_visible, soup.findAll(text=True)) if len(t.split()) > 10]
    texts.extend(visible_texts)

    # youtube texts
    yt_desc = soup.find_all("span", {"class": "yt-core-attributed-string yt-core-attributed-string--white-space-pre-wrap"})
    if yt_desc:
        texts.append(clean_text(yt_desc[-1].get_text()))

    yt_comments = [clean_text(c.get_text()) for c in soup.find_all("yt-formatted-string", {"class": "style-scope ytd-comment-renderer"}) if c]
    texts.extend(yt_comments)

    return " ".join(texts)

# def pdf2text(httpx_PDF_response):
#     with io.BytesIO(httpx_PDF_response.content) as pdf_file:
#         text = ""
#         with fitz.open(filetype="pdf", stream=pdf_file.read()) as doc:
#             for p in list(range(0, min(PDF_PAGES_MAX, doc.page_count), 1)):
#             # for p in doc[:min(PDF_PAGES_MAX, doc.page_count)]:
#                 page = doc.load_page(p)
#                 text = text + " " + str(page.get_text())
#     lines = []
#     for line in text.split("\n"):
#         if len(line) > 20:
#             lines.append(line.strip())
#     return clean_text(" ".join(lines))

def pdf2text(httpx_PDF_response):
    """
    Convert a PDF file to text.

    Args:
        httpx_PDF_response (httpx.Response): The HTTP response containing the PDF file.

    Returns:
        str: The extracted text from the PDF file.
    """
    with io.BytesIO(httpx_PDF_response.content) as pdf_file:
        with fitz.open(filetype="pdf", stream=pdf_file.read()) as doc:
            page_texts = [str(doc.load_page(p).get_text()) for p in range(min(PDF_PAGES_MAX, doc.page_count))]
            text = " ".join(page_texts)

    lines = [line.strip() for line in text.split("\n") if len(line) > 20]
    return clean_text(" ".join(lines))

# async def url2text(url, pw_session, pw_browser, httpx_session, semaphore):
#     if url == 'https://www.cnn.com/2023/03/12/investing/stocks-week-ahead/index.html':
#         pass
#     async with semaphore:
#         # async with pw_session:
#         page = await pw_browser.new_page()
#         await stealth_async(page)
#         try:
#             # try playwright stealth for html
#             pw_response = await page.goto(url, wait_until="domcontentloaded")

#             # if not pw_response.ok:
#             #     return {url: ""}

#             if "html" in pw_response.headers.get("content-type"):
#                 # simulate mousescoll, needed to retrieve dynimcally generate youtube content(i.e. description and comments)
#                 title = await page.title()
#                 if "youtube" in title.lower():
#                     n_scroll = 5
#                     for i in range(5):
#                         page.mouse.wheel(0, 15000)
#                         time.sleep(0.5)
#                         i += 1
#                 html = await page.content()
#                 text = html2text(html)
#                 await page.close()
#                 if text:
#                     logging.info(f"ok txt retrieved {url}")
#                     return {url: text}
#                 else:
#                     logging.info(f"no txt retrieved {url}")
#                     return {url: ""}
#         except:
#             await page.close()
#             # fallback to httpx
#             try:
#                 # async with httpx_session.get(url) as httpx_response:
#                 httpx_response = await httpx_session.get(url)
#                 if "html" in httpx_response.headers["content-type"]:
#                     if httpx_response.text:
#                         logging.info(f"ok txt retrieved {url}")
#                         return {url: html2text(httpx_response.text)}
#                 else:
#                     # content-type is not always set corrently on response.headers, so we assume PDF content and try to extract text.
#                     text = pdf2text(httpx_response)
#                     if text:
#                         logging.info(f"ok txt retrieved {url}")
#                         return {url: text}
#                     else:
#                         logging.info(f"fail txt retrieved {url}")
#                         return {url: ""}

#             except Exception as e:
#                 logging.info(f"fail txt retrieved {url}")
#                 return {url: ""}

async def url2text(url, pw_session, pw_browser, httpx_session, semaphore):
    """
    Retrieve text content from a given URL.

    Args:
        url (str): The URL to retrieve text from.
        pw_session: The Playwright session.
        pw_browser: The Playwright browser.
        httpx_session: The HTTPX session.
        semaphore: The semaphore for concurrency control.

    Returns:
        dict: A dictionary containing the URL as the key and the retrieved text as the value.
    """
    N_SCROLLS = 5
    SCROLL_DISTANCE = 15000

    async def retrieve_text(content, source):
        """
        Retrieve text from the content based on the source type.

        Args:
            content: The content to retrieve text from.
            source: The source object.

        Returns:
            dict: A dictionary containing the URL as the key and the retrieved text as the value.
        """
        text = html2text(content) if "html" in source.headers["content-type"] else pdf2text(source)
        if text:
            logging.info(f"ok txt retrieved {url}")
            return {url: text}
        else:
            logging.info(f"fail txt retrieved {url}")
            return {url: ""}

    if url == 'https://www.cnn.com/2023/03/12/investing/stocks-week-ahead/index.html':
        pass

    async with semaphore:
        page = await pw_browser.new_page()
        await stealth_async(page)
        try:
            pw_response = await page.goto(url, wait_until="domcontentloaded")
            if "html" in pw_response.headers.get("content-type"):
                title = await page.title()
                if "youtube" in title.lower():
                    for _ in range(N_SCROLLS):
                        page.mouse.wheel(0, SCROLL_DISTANCE)
                        time.sleep(0.5)
                html = await page.content()
                text = await retrieve_text(html, pw_response)
                if not text:
                    text = ""
                return text
        except Exception as e:
            logging.error(f"Playwright error: {e}")
        finally:
            await page.close()

        try:
            httpx_response = await httpx_session.get(url)
            text = await retrieve_text(httpx_response.text, httpx_response)
            if not text:
                text = ""
            return text

        except Exception as e:
            logging.error(f"HTTPX error: {e}")
            return {url: ""}


# async def urls2text(urls, max_crawl_concurrency):
#     semaphore = asyncio.Semaphore(max_crawl_concurrency)
#     pw_session = await async_playwright().start()
#     pw_browser = await pw_session.chromium.launch_persistent_context(
#         "/tmp", headless=True, timeout=10000, no_viewport=True, 
#     )
#     # pw_browser = await pw_session.chromium.launch_persistent_context(
#     #     "/tmp", headless=True, timeout=10000, 
#     # )
    
#     httpx_session = httpx.AsyncClient()

#     tasks = [
#         url2text(url, pw_session, pw_browser, httpx_session, semaphore) for url in urls
#     ]
#     list_of_dicts = await asyncio.gather(*tasks)
    
#     for d in list_of_dicts: 
#         if not d:
#             list_of_dicts.remove(d)

#     result = {k: (v if v is not None else "") for d in list_of_dicts for k, v in d.items()}
    
#     await pw_browser.close()
#     return result

async def urls2text(urls, max_crawl_concurrency):
    """
    Fetches text content from a list of URLs concurrently using Playwright and HTTPX.

    Args:
        urls (list): A list of URLs to fetch text content from.
        max_crawl_concurrency (int): The maximum number of concurrent crawls.

    Returns:
        dict: A dictionary containing the fetched text content, with URLs as keys and text as values.
    """
    semaphore = asyncio.Semaphore(max_crawl_concurrency)

    async with async_playwright() as pw_session:
        pw_browser = await pw_session.chromium.launch_persistent_context(
            "/tmp", headless=True, timeout=10000, no_viewport=True, 
        )

        async with httpx.AsyncClient() as httpx_session:
            tasks = [
                url2text(url, pw_session, pw_browser, httpx_session, semaphore) for url in urls
            ]
            list_of_dicts = await asyncio.gather(*tasks)

    list_of_dicts = [d for d in list_of_dicts if d]
    result = {k: (v if v is not None else "") for d in list_of_dicts for k, v in d.items()}

    #   await pw_browser.close()
    return result


@shared_task(
    name="ingress:job_crawl",
    bind=True,
    priority=5,
    default_retry_delay=30,
    max_retries=3,
    soft_time_limit=10000,
)
def source_text(self, job_id, source_ids):
    """
    Extracts text from the given sources and updates their status and text properties.

    Args:
        job_id (int): The ID of the job.
        source_ids (list): A list of source IDs.

    Returns:
        int: The ID of the job.

    Raises:
        Exception: If an error occurs during the text extraction process.
    """
    try:
        # load job
        job = ~Job.get(job_id)
        if job.status == "failed":
            return job_id

        # load sources
        sources = [~Source.get(sid) for sid in source_ids]
        sources = [s for s in sources if s.text != ""]

        # get texts
        urls = [source.url for source in sources]
        shuffle(urls)
        url2text = async_to_sync(urls2text)(urls, TEXT_CRAWL_CONCURRENCY)

        # update sources
        forbidden_words = {"cloudflare", "robot", "captcha", "cloudfront"}

        for source in sources:
            tokens = url2text[source.url].split()
            source.text = " ".join(tokens[:TEXT_TOKEN_MAX])
            source.text_token = len(tokens[:TEXT_TOKEN_MAX])

            if any(word.lower() in forbidden_words for word in tokens) or source.text_token < TEXT_TOKEN_MIN:
                source.status = "failed"
            else:
                source.status = "done"

            source.save()

    except Exception as e:
        job.status = "failed"
        job.save()
        logging.error(f"job {job.id}: failed, source_text, {e}")

    return job_id