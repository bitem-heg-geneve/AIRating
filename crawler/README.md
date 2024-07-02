# crawler

Crawls news and organizations websites with CommonCrawl.

data repository
 - data/organizations.txt : tab separated file, with source ID, source name, and source base URL, for organizations
 - data/news.txt : tab separated file, with source ID, source name, and source base URL, for news sites
 - data/cc_monthly_indexes.txt : space separated files with CommonCrawl indexes to consider.

CommonCrawl
Commoncrawl delivers monthly indexes. These indexes can be found on https://commoncrawl.org/get-started.
Each index can be queried with a specific domain name, and will return metadata about all crawled webpages for this domain. When multiple indexes are present, the most recent version for each webpage will be considered (or not if a webpage was last indicated as deleted). Then, all these webpages can be crawled by amazon cloud.

Workflow
Priorly : indicate in data files the news and organization your want to crawl, and the indexes to query.
1_download_ccindexes.py : creates a ccindexes/ path. Then, for each CC index (e.g. 2024-26), creates a path for downloading metadata for each website (i.e. news or organizations).
2_make_ccmasters.py : from the previously downloaded files, creates uniques master files for each website, keeping only the last version when multiple indexes are queried.
3_download.py : from the previously created master files, download CommonCrawl archives (warc.gz format)
4_extract_pages.py : extract pages from warc archives. By default, create a crawled_contents.json file with metadata and extracted text (BeautifulSoup) for all webpages... but of course any individual crawled_content can be exploited to store a database (e.g. MongoDB) or a search engine (e.g. Elastic).