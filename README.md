# Web Scrapping using Python & Scrapy on Daft.ie
## This repo contains the project resulting from [this](https://www.youtube.com/watch?v=cPx621bqgkY&t=14s) Youtube tutorial.

It consists basically on fetcing information about rent price, location, size and number of views for each comercial property listed a the daft.ie website. This info is fetched using XPath reference.

The video did not cover how to add the MongoDB pipeline to the project, although the source code can be found on the blog-link listed below.

[Blog page](https://www.cryt.ie/blogs/Scrapy.html) containing further info about the tutorial. 
______________________________________________________________________________________________________________________________

Although the source code for the original project is available [here](https://github.com/avacadoadam/Webscraping-tutorial), I couldn't make my scrapper work.

Scraper is now working, except for the Location column [possible error on XPath] that is returning 'null'.

The command ```scrapy crawl daft -t csv -o data.csv``` generates an empty .csv file (available at [data.csv](https://github.com/laisbsc/webScrappingDaft/blob/master/data.csv)) instead of outputting the scrapped data from the website.

Further features to be implemented on this project:
 - use Postman to improve the structure of the website;
 - ~~use MongoDB pipeline to automate the insertion of data into the output file [DONE];~~
 - use matplotlib to visualise the most significant insights from the scrapped data (data science).
 
UPDATE I(04/02/2020): [Adam](https://github.com/avacadoadam/webScrappingDaft) updated this README.md with a list of possible debugs for the application. 

# Possible solutions to no output:

## Checking Command used in log.
(ENV) (base) C:\Users\laisb\python-virtual-environments\scrapyTutorial\scrapyWebTut>scrapy crawl daft -t csv -o data.csv
*The command is correct.*

## Splash reading robots.txt bug
```python
2020-02-02 20:36:01 [scrapy.core.engine] DEBUG: Crawled (200) <GET https://www.daft.ie/robots.txt> (referer: None)
2020-02-02 20:36:01 [scrapy.downloadermiddlewares.retry] DEBUG: Retrying <GET http://0.0.0.0:8050/robots.txt> (failed 1 times): An error occurred while connecting: 10049: The requested address is not valid in its context..
2020-02-02 20:36:02 [scrapy.downloadermiddlewares.retry] DEBUG: Retrying <GET http://0.0.0.0:8050/robots.txt> (failed 2 times): An error occurred while connecting: 10049: The requested address is not valid in its context..
2020-02-02 20:36:02 [scrapy.downloadermiddlewares.retry] DEBUG: Gave up retrying <GET http://0.0.0.0:8050/robots.txt> (failed 3 times): An error occurred while connecting: 10049: The requested address is not valid in its context..
```
It is interesting that the downladermiddlewares tries to access www.daft.ie robots.txt through http://0.0.0.0:8050. This only occurs when using splashRequest. There are workarounds however which can be found in https://github.com/scrapy-plugins/scrapy-splash/issues/180. Which involves changing the build order.
However I do not believe this is the issue you face, but this can be debugged by setting ROBOTSTXT_OBEY to False in settings.py 
and check if the result is differnet.
```
ROBOTSTXT_OBEY = False
```
On my Env I did not need to.


## Possible Splash configuration Error:

When I turned off my splash service my output was similar to yours.
splash uses docker and on linux the command is 
```
sudo docker run -p 8050:8050 scrapinghub/splash
```
https://docs.docker.com/engine/installation/windows/ to setup docker on windows.
*I added a note to add documentation for windows installation on the scrapy-splash repo*

To check if splash is running visit the http://127.0.0.1:8050/ on a browser where you should see a 
webpage that looks like 

![alt text](https://github.com/avacadoadam/webScrappingDaft/blob/master/splashWebpageExample.png)

*I believe this may be the issue*
*UPDATE (04/02/20): This was the issue. I had the wrong port and docker was also a bit flaky. Fixed port and repaired Docker, crawler works! :D

## Also included a slight code update
The code in parse function in /spiders/daft.py
```python
        yield rent_price
        yield location
        yield size
        yield how_many_times_views
```
Should return a Request, BaseItem, dict or None
So I updated it to 
```python
        yield {
            'rent_price': rent_price,
            'location': location,
            'size': size,
            'how_many_times_views': how_many_times_views
        }
```
hope that helps!
scrapy : 1.8.0
OS: Ubuntu 18.04.2 LTS
Splash v3.3.1

I used:
Scrapy :  1.8.0 - projectscrapyWebTut
OS: Win 10 Pro v. 1809
Python: 3.7.0
__________________________________________________________________

# MongoDB pipeline
## Instructions on how to add it to the crawler

MongoDB is NoSQL that has a very fluid development process with scrapy and python.

To note we do not need to configure the database in mongodb or create it the pymongo libary will do it for us.

A example of data I scraped and host in mongoDB can be see here 
https://cryt.ie/API/api.html#view_data

To begin we will add two variables to the scrapy settings file
```python
MONGO_URI = 'mongodb://localhost:27017'
MONGO_DATABASE = 'daft'
```

We will then uncomment 
```python
ITEM_PIPELINES = {
   'scrapyWebTut.pipelines.ScrapywebtutPipeline': 300,
} 
```

in the *settings.py* we need to activate the pipeline, the number is the ID and will decide what pipelines get executed first.

the URI will points to mongo database
*I presume you will use mongoDB localy and not configure security measures for testing and development*
The database name is daft and is where we will store the data.

Will we need the libary *pymongo* which can be installed with pip. And on pipelines.py
```python
import pymongo
```

In the pipeline ScrapywebtutPipeline
We will override the __init__ method
```python
    def __init__(self, mongo_uri, mongo_db, stats):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.stats = stats
```
This will simply set the variables from the settings file.

However we need to also override from_crawler which has access the the scrapy env and settings we set
```python
   @classmethod
    def from_crawler(cls, crawler):
        ## pull in information from settings.py
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE'),
            stats=crawler.stats
        )
``` 
This will be called by the scrapy framework BEFORE __Init__ and then call init with the params we give.
This is standard and can be used for all your projects working with mongoDB

After we will override the open_spider method and init the pymongo libary and connection to the database
```python
def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
```
This is following the life cycle design pattern scrapy uses.

Now we will also override close_spider 
```python
    def close_spider(self, spider):
        self.client.close()
```
by simply closing the database connection.

Now we will we get to the process_item(self,item,spider) function.
Where we can filter, process and then store the data in our mongoDB
In the case of this project we know the item will be a dict 
```python
    yield {
            'rent_price': rent_price,
            'location': location,
            'size': size,
            'how_many_times_views': how_many_times_views
        }
```
Data won't be processed or filtered but simply inserted into the mongoDB.
We will insert into the collection called "properties" inside the daft database using the connection we set up ealier.
We will also return the item as we may add more pipelines that come after the mongoDB such as adding it to a MYSQL data etc..
not returning the item tells scrapy that you want to discard it and can cause annoying logic bugs.

```python
  def process_item(self, item, spider):
        self.db['properties'].insert(item)
        return item
```
And that is it. We now stored the data in our mongoDB.

To the data in mongo through the cmd
We use the commands

```
mongo
show dbs
use daft
show collections
db.properties.find().pretty()
```

![alt text](https://github.com/avacadoadam/webScrappingDaft/blob/master/mongoDbexample.png)

Pipelines are very handy as we can create differnet ones to do differnet things and reuse them in other projects
A example may be 

FilterDataPipeline: 10
AddDataThroughAIModalPipeline: 100
AddDataToMongoDBPipeline: 110
EmailDataToMePipeLine: 120


Feel free to ask any questions or another scraping project you would like help with!
