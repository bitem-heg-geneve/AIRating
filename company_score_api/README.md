# API description
This API takes (1) a json document that links a URL to a Named Entity (NE)/count dictionnary and (2) a list of companies for which we want to allocate a score.

# Code
In order to get the app working:
```
cd $WD
python3.10 -m venv env
source env/bin/activate
pip install -r requirements.txt
flask run --host=0.0.0.0
```

# Current demo inputs and ouputs
In this demos, the model takes the following input format for the NE/count dictionary:
```
{
    "https://www.epa.gov/newsreleases/search/field_geographic_locations/california/field_geographic_locations/massachusetts/subject/emergency-response/subject/radiation/year/2017/year/2018": {
        "EPA": 12,
        "US EPA": 2,
        "FOIA": 1,
        "Jobs Newsroom": 1,
        "White": 1,
        "EPA Web": 1,
        "United States Environmental Protection Agency": 1,
        "EPAEPA": 1,
        "Current Leadership": 1,
        "Brownfields": 3,
        "EPA Newsroom": 1
    },
    "https://www.epa.gov/newsreleases/search/field_geographic_locations/connecticut/field_geographic_locations/rhode-island/field_press_office/headquarters/field_press_office/region-01/subject/awards-and-recognition/subject/hazardous-waste": {
        "Jobs Newsroom": 1,
        "White": 1,
        "EPA": 13,
        "US EPA": 2,
        "FOIA": 1,
        "EPA Web": 1,
        "United States Environmental Protection Agency": 1,
        "EPAEPA": 1,
        "Connecticut": 1,
        "Rhode Island": 2,
        "Environmental": 1,
        "U.S. EPA": 2,
        "National Grid": 1,
        "ENERGY": 1,
        "Warren": 1
    }
}
```
And a list of company:
```
['Chevron', 'HSBC', 'Nestlé', 'Apple', 'Volkswagen', 'Allianz', ...]
```

It outputs the following results formats:
```
{
    "https://ourworldindata.org/grapher/internally-displaced-persons-from-disasters?tab=chart&country=MWI": {
        "Allianz": 0.2542268931865692
    },
    "https://ourworldindata.org/grapher/humanitarian-aid-received?tab=chart&country=BLZ": {
        "Allianz": 0.2542268931865692
    },
    "http://blogs.worldbank.org/africacan/climatechange/trade/education/jobs/dev4peace/comment/reply/2546": {
        "Bank of America": 0.13395746052265167,
        "Deutsche Bank": 0.1328144520521164,
        "Royal Bank of Canada": 0.12377194315195084,
        "Westpac Banking": 0.12252455949783325
    }
}
```
