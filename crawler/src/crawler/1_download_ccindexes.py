import datetime,re,json,os,requests

from functions import load_news_and_organizations
from params import *

compagnies = load_news_and_organizations(NEWS_FILE,ORGAS_FILE)

print("news and organizations read")
print(len(compagnies)," websites to crawl")


# load errors 404
# errors 404 during previous commoncrawl index collection
# means no commoncrawl content for this company and this index
# -> no need to retry

errors404 = {}
if (os.path.isfile("data/errors_indexes.txt")) :
    rfile = open("data/errors_indexes.txt","r",encoding="utf-8")
    for line in rfile :
        cols = line.strip().split("\t")
        i = cols[1]
        index = cols[0]
        error = cols[2]
        if (error == "404") :
            errors404[index+"_"+i] = 1 # errors 404 are index and company dependent
        rfile.close()
        
print("errors 404 read")

# load cc indexes
# indexes are monthly batches in cc
# this file can be edited year after year
indexes = []
rfile = open(CC_MONTHLY_INDEXES,"r",encoding="utf-8")
for line in rfile :
    match = re.search(r"^(\d+-\d+)",line)
    if (match) :
        indexes.append(match.group(1))
rfile.close()

print("cc monthly indexes read")

# time for crawling indexes
# indexes are stored in cc_indexes/ path
try :
    os.mkdir("cc_indexes")
except:
    pass

errors = 0

for i in indexes :
    try :
        os.mkdir("cc_indexes/"+i)
    except:
        pass
    print(str(datetime.datetime.now())[:19],i)
    for c in compagnies :
        if (os.path.isfile("cc_indexes/"+i+"/"+ str(c["id"])+"_" + i + ".json")) :
            # index is already crawled and present
            continue
        if ((i + "_" + str(c["id"]) in errors404)) :
            # we know there was a 404 error, so no index for this one
            continue

        # building cc query and requesting
        cc_url = "http://index.commoncrawl.org/CC-MAIN-"+i+"-index?"
        cc_url += "url="+c["domain"]+"&matchType=domain&output=json"
        try :
            response = requests.get(cc_url)

            # response analyzing and writing in cc_indexes repositories
            if response.status_code == 200 :
                # response ok
                wfile = open("cc_indexes/"+i+"/"+ str(c["id"])+"_" + i + ".json","w",encoding="utf-8")
                record_list = []
                records = response.content.splitlines()
                for record in records:
                    record_list.append(json.loads(record))
                wfile.write(json.dumps(record_list,indent=2))
                wfile.close()
            else :
                # response not ok -> store in errors.txt
                # if error was 404, it means that there is no content
                # else, the index will be crawled in another execution
                lfile = open("data/errors_indexes.txt","a",encoding="utf-8")
                lfile.write(i+"\t"+str(c["id"])+"\t"+str(response.status_code)+"\n")
                lfile.close()
                errors += 1
        except Exception as e :
            print(cc_url)
            print(e)

print("All CommonCrawl indexes downloaded")
if (errors > 0) :
    print(errors,"errors, please check data/errors_indexes.txt")
    
