import datetime,re,json,os,requests

from functions import load_news_and_organizations
from params import *

compagnies = load_news_and_organizations(NEWS_FILE,ORGAS_FILE)

print("news and organizations read")

# load cc indexes
indexes = []
rfile = open(CC_MONTHLY_INDEXES,"r",encoding="utf-8")
for line in rfile :
    match = re.search(r"^(\d+-\d+)",line)
    if (match) :
        indexes.append(match.group(1))
rfile.close()

print("cc monthly indexes read")

try :
    os.mkdir("cc_masters")
except:
    pass

status = {}
for c in compagnies :
    urls = {}
    for i in indexes :
        if (os.path.isfile("cc_indexes/"+i+"/"+ str(c["id"])+"_" + i + ".json")) :
            rfile = open("cc_indexes/"+i+"/"+ str(c["id"])+"_" + i + ".json","r",encoding="utf-8")
            webpages = json.loads(rfile.read())
            rfile.close()
            for w in webpages :
                if ("mime-detected" in w) :
                    if (not ((w["mime-detected"].lower() == "text/html") or (w["mime-detected"].lower() == "application/pdf"))) :
                        continue
                if ("languages" in w) :
                    if (not ("eng" in w["languages"])) :
                        continue
                urls[w["url"]] = w
    wfile = open("cc_masters/"+str(c["id"])+"_master.json","w",encoding="utf-8")
    wfile.write(json.dumps(urls,indent=2))
    wfile.close()

print("masters compiled")
