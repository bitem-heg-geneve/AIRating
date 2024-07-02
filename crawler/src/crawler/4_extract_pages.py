from warcio.archiveiterator import ArchiveIterator
from bs4 import BeautifulSoup
import re,os,datetime,json
from shutil import copyfile

from functions import load_news_and_organizations
from params import *

compagnies = load_news_and_organizations(NEWS_FILE,ORGAS_FILE)

print("compagnies read")

masters = os.listdir("cc_masters")

crawled_contents = [] # final output

for file in masters :
    
    cid = file[:5] # company nid
    
    # retrieve company name
    company_name = ""
    for c in compagnies :
        if (c["id"] == int(cid)) :
            company_name = c["name"]
    print("Treating",cid,company_name)

    # load URLs
    rfile = open("cc_masters/"+file,encoding="utf-8")
    webpages = json.loads(rfile.read())
    rfile.close()

    i = 0
    for url,w in webpages.items() :
        i += 1
        if (i % 100 != 0) :
            continue
        
        # filter with metadata
        if (w["status"] != "200") :
            continue

        # retrieve paths for crawling
        dirs = w["filename"].split("/")
        filename = dirs[-1]
        if not os.path.isdir("cc_gzfiles/"+cid) :
            os.mkdir("cc_gzfiles/"+cid)
        temp_path = "cc_gzfiles/"+cid+"/"
        for d in dirs :
            if (d == "crawl-data") :
                continue
            if (d == "segments") :
                continue
            if (d == "warc") :
                continue
            if (d == filename) :
                break
            if not os.path.isdir(temp_path+d) :
                os.mkdir(temp_path+d)
            temp_path += d + "/"

        if (os.path.isfile(temp_path + filename)) :            
            # extract the text
            try :
                with open(temp_path + filename, 'rb') as stream:
                    for record in ArchiveIterator(stream):
                        if (mime_detected.lower() == "text/html") :
                            text = record.content_stream().read().decode("utf-8")
                            soup = BeautifulSoup(text)
                            source_type = "news"
                            if (int(cid) > 19000) :
                                source_type = "organizations"
                            HTML_text = soup.get_text()
                            HTML_text = re.sub(r"\n+","\n",HTML_text)
                            crawled_content = {"_id":url,"mime":w["mime"],"mime-detected":["mime_detected"],"source_type":source_type,
                                      "name":compagnies[cid]["name"],
                                      "HTML_year":int(w["timestamp"][:4]),"languages":w["languages"],"url":url,
                                      "text":HTML_text}
                            crawled_contents.append(crawled_content)
                            
            except Exception as e :
                efile = open("errors_extract.txt","a",encoding="utf-8")
                efile.write(url+"\t"+str(e)+"\n")
                efile.close()
                
with open("crawled_contents.json","w",encoding="utf-8") as wfile :
    wfile.write(json.dumps(crawled_contents,indent=2))


