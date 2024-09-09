# API description
This API takes a list of json documents where each json has both a "url" and a "text" feature. It then run a Named Entity Recognition (NER) model on the text to output a json document that links each url to a NE/count dictionnary.
The output of this API will then go into the company score API along with a company list.

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
In this demos, the model takes the following input format:
```
[{'url': 'url1',
     'text': 'THIS IS THE CONTENT OF THE DOCUMENT NUMBER 1 wich speak about ABOUT Coca Cola'},
    {'url': 'url2',
     'text': 'THIS IS THE CONTENT OF THE DOCUMENT NUMBER 2 ABOUT also about the company Coca Cola.'
             ' But not only because it speaks also about the company Bank of America.'},
    {'url': 'url3',
     'text': 'THIS IS THE CONTENT OF THE DOCUMENT NUMBER 1 wich speak about ABOUT BMW'},
    {'url': 'url4',
     'text': 'THIS IS THE CONTENT OF THE DOCUMENT NUMBER 2 ABOUT also about the company Renault.'
             ' But not only because it speaks also about the company Renault.'}]
```

It outputs the following results formats:
```
{
"url1":{"Coca Cola":1},
"url2":{"Bank of America":1,"Coca Cola":1},
"url3":{"BMW":1},
"url4":{"Renault":2}
}
```