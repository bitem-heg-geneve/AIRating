import datetime,re,json,os,requests,time

from functions import load_news_and_organizations
from params import *

try :
    os.mkdir("cc_gzfiles")
except:
    pass

i = 0

masters = os.listdir("cc_masters")
for file in masters :
    cid = file[:5]
    print("Treating",file)
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
        
        # create paths for crawling
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
            
        # crawl
        print("\t"+w["filename"])
        if (not(os.path.isfile(temp_path + filename))) :
            offset_end = str(int(w["offset"]) + int(w["length"]) - 1)
            try :
                resp = requests.get(CC_ENDPOINT + w["filename"], headers={'Range': 'bytes={}-{}'.format(w["offset"], offset_end)})
                time.sleep(2)
                gzfile = open(temp_path + filename,"wb")
                gzfile.write(resp.content)
                gzfile.close()
                print("\tdownloaded")
            except Exception as e :
                efile = open("errors_download_"+cid+".txt","a",encoding="utf-8")
                efile.write(w["filename"]+"\t"+str(e)+"\n")
                efile.close()
        else :
            print("\there")




