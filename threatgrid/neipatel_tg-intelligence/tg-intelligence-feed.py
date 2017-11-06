#!/usr/bin/python
import json
import sys
import requests
import datetime

#make an array of dates for given number of days
def makeDates(days):
    dates = []
    while days > 0:
        now = datetime.datetime.now()
        dateFormat = '%Y-%m-%d'
        date = (now-datetime.timedelta(days=days)).strftime(dateFormat)
        dates.append(date)
        days -= 1
    return dates


def get(url):
    try:
        response = requests.get(url)
        # Consider any status other than 2xx an error
        if not response.status_code // 100 == 2:
            return "Error: Unexpected response {}".format(response)
        try:
            return response.json()
        except:
            return "Error: Non JSON response {}".format(response.text)
    except requests.exceptions.RequestException as e:
        # A serious problem happened, like an SSLError or InvalidURL
        return "Error: {}".format(e)

#enter api key here
api_key = ""

#-----------LIST OF AVAILIBLE FEEDS TO PULL FROM-----------#
feedNames = ['banking-dns','dll-hijacking-dns','doc-net-com-dns','downloaded-pe-dns',
            'dynamic-dns','irc-dns','modified-hosts-dns','parked-dns','public-ip-check-dns',
            'ransomware-dns','rat-dns','sinkholed-ip-dns']

days = 10
dates = makeDates(days)
feedURLs={}
for feed in feedNames:
	feedURLs[feed] = {}
	for date in dates:
		JSONURL = 'https://panacea.threatgrid.com/api/v3/feeds/{}_{}.json?api_key={}'.format(feed,date,api_key)
		feedURLs[feed][date] = JSONURL


#-----------HAVE USER SELECT WHAT FEED THEY WOULD LIKE TO COLLECT DATA FOR-----------#

for a in range(len(feedNames)):
	print str(a+1)+". " + feedNames[a]

feed_selection = int(raw_input("What feed would you like to get? (1-11) "))
feed_selection = feed_selection-1

#-----------BUILD THE LIST OF URLS THAT NEED TO BE QUERED-----------#
query_urls = []
for date in dates:
	query_urls.append(feedURLs[feedNames[feed_selection]][date])

#initialize empty arrays 
domains = []
shas = []

for url in query_urls:
	response = get(url)
	for a in range (len(response)):
		domains.append(response[a]["domain"])
		shas.append(response[a]["sample_sha256"])
#better way than before
domains = set(domains)

#-----------WRITE OUTPUTS TO FILES FOR USE IN LATER SECTIONS-----------#

domain_file = open(feedNames[feed_selection]+'_domains','w')
sha_file = open(feedNames[feed_selection]+'_shas','w')

for domain in domains:
	domain_file.write("%s\n" % domain)

for sha in shas:
	sha_file.write("%s\n" % sha)

domain_file.close()
sha_file.close()
