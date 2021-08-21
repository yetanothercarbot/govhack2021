'''
Process the CSVs from the open data portal and export into the postgresql database.

To minimize memory usage for large files (such as the crash location files),
the data will be processed as it is downloaded and processed in batches of
100 records into the postgresql database.

The datasets being used are:

- Road crash locations
- Road census data
'''
import json
import requests
from contextlib import closing
import csv

ROAD_CENSUS_URLS = {
    2009: "http://www.tmr.qld.gov.au/-/media/aboutus/corpinfo/Open%20data/trafficcensus/trafficcensus2004-2009.csv",
    2010: "http://www.tmr.qld.gov.au/~/media/aboutus/corpinfo/Open%20data/trafficcensus/trafficcensus2010csv.csv",
    2011: "http://www.tmr.qld.gov.au/~/media/aboutus/corpinfo/Open%20data/trafficcensus/trafficcensus2011csv.csv",
    2012: "http://www.tmr.qld.gov.au/~/media/aboutus/corpinfo/Open%20data/trafficcensus/trafficcensus2012.csv",
    2013: "http://www.tmr.qld.gov.au/~/media/aboutus/corpinfo/Open%20data/trafficcensus/traffic_census_2013.csv",
    2014: "http://www.tmr.qld.gov.au/~/media/aboutus/corpinfo/Open%20data/trafficcensus/trafficcensus2014.csv",
    2015: "http://www.tmr.qld.gov.au/-/media/aboutus/corpinfo/Open%20data/trafficcensus/trafficcensus2015.csv",
    2016: "http://www.tmr.qld.gov.au/-/media/aboutus/corpinfo/Open%20data/trafficcensus/trafficcensus2016_csv.csv",
    2017: "http://www.tmr.qld.gov.au/-/media/aboutus/corpinfo/Open%20data/trafficcensus/trafficcensus2017.csv",
    2018: "http://www.tmr.qld.gov.au/-/media/aboutus/corpinfo/Open%20data/trafficcensus/trafficcensus2018.csv",
    2019: "https://www.data.qld.gov.au/dataset/5d74e022-a302-4f40-a594-f1840c92f671/resource/dc82ec39-4513-437c-8d07-ecb08474a065/download/trafficcensus2019.csv",
    2020: "https://www.data.qld.gov.au/dataset/5d74e022-a302-4f40-a594-f1840c92f671/resource/1f52e522-7cb8-451c-b4c2-8467a087e883/download/trafficcensus2020.csv",
}

ROAD_CRASHED_URL: "https://www.data.qld.gov.au/dataset/f3e0ca94-2d7b-44ee-abef-d6b06e9b0729/resource/e88943c0-5968-4972-a15f-38e120d72ec0/download/1_crash_locations.csv"


settings = {}

# Read SQL Auth data
with open('settings.json') as json_file:
    settings = json.load(json_file)



