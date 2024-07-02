import re

def load_news_and_organizations(news_path,orga_path) :
    # output variable
    compagnies = []

    # load organizations
    rfile = open(news_path,"r",encoding="utf-8")
    for line in rfile :
        if (line.startswith("#")) : # comment
            continue
        company = {}
        cols = line.strip().split("\t")
        i = int(cols[0]) # news id -> starts from 10000
        name = cols[1] # news name
        url = cols[2] # home page
        if (url == "NULL") :
            continue

        # cleaning domain
        domain = url.replace("https://","")
        domain = domain.replace("http://","")
        domain = re.sub(r"\/$","",domain)

        # make record
        company = {"id" : i,
                   "name" : name,
                   "domain" : domain}

        # append record
        compagnies.append(company)
    rfile.close()

    # load orgas
    rfile = open(orga_path,"r",encoding="utf-8")
    for line in rfile :
        if (line.startswith("#")) : # comment
            continue
        company = {}
        cols = line.strip().split("\t")
        i = int(cols[0]) # orga id -> starts from 20000
        name = cols[1] # orga name
        url = cols[2] # home page
        if (url == "NULL") :
            continue

        # cleaning domain
        domain = url.replace("https://","")
        domain = domain.replace("http://","")
        domain = re.sub(r"\/$","",domain)

        # make record
        company = {"id" : i,
                   "name" : name,
                   "domain" : domain}

        # append record
        compagnies.append(company)
    rfile.close()

    return compagnies
