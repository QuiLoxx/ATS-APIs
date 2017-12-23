# This script will request feeds and dump them to stdout as received. It reads
# a config file, by default ./TGiFeeds.cfg, to get hostname, feed, and API key
# information.
#



import logging, requests, sys, configparser, datetime, argparse

def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)
    
def getopts(argv):
    parser = argparse.ArgumentParser(
        description='Retrieve threat intel feeds from Cisco Threat Grid',
        epilog='''This script can be used to retrieve threat intel feeds from the Cisco Threat Grid API.
            It reads configuration paramaters from the command line, and defaults from a configuration file.
            Usage of this script requires a valid API key. This utility is provided as an example, and with
            no guarantees or support options.''' 
        )
    parser.add_argument('-a', '--after_time',
                        help='''Specify a start time for the feed window. You want the data from after this time. Must be in format "%%Y-%%m-%%dT%%H:%%M:%%SZ".
                            (default one hour ago, or one hour before before_time if specified)''',
                        type=valid_date)
    parser.add_argument('-b', '--before_time',
                        help='''Specify an end time for the feed window. You want the data from before this time. Must be in format "%%Y-%%m-%%dT%%H:%%M:%%SZ".
                            (default now, or one hour after after_time if specified)''',
                        type=valid_date)
    parser.add_argument('-c', '--cfg_file', help='specify a configuration file (default %(default)s))',
                        type=argparse.FileType('r'), default='TGiFeeds.cfg')
    parser.add_argument('-e', '--experiment', help='Do everything except request the feed. Most useful with -v',
                        action='store_true')
    parser.add_argument('-k', '--api_key', help='specify an API key value (overrides config file)')
    parser.add_argument('-l', '--log_file', help='specify a log file (overrides config file)')
    parser.add_argument('-m', '--feed_menu', help='print out the menu of available feeds and exit TODO')
    parser.add_argument('-o', '--out_file', help='specify an output file (default STDOUT)',
                        type=argparse.FileType('w'), default=sys.stdout)
    parser.add_argument('-p', '--parameters', help='specify additional parameters as a single string TODO')
    parser.add_argument('-s', '--server_name', help='specify a server hostname (overrides config file)')
    parser.add_argument('--rtfm', help='''print a link to the API documentation for the specified feed and exit
                                        (Threat Grid account required)
                                        If no feed is specified it will print out links for all feed types''',
                        action='store_true')
    parser.add_argument('-v', '--verbose', help='print diagnostic and troubleshooting information to stdout', action='store_true')
    parser.add_argument('feedName', nargs='?', help = 'specify the desired feed', default=None)
    
    args = parser.parse_args()
    return(args)

def myget(url,QS):
    try:
        r = requests.get(url,params=QS)
        if args['verbose'] is True: print('Request URL:', r.url,'\n')
        if r.status_code // 100 != 2:
            return "Error: {}".format(r)
        try:
            return r.json()
        except:
            return "Error: Non JSON response - {}".format(r.text)
    except requests.exceptions.RequestException as e:
        return 'Error: Exception - {}'.format(e)


def errors(response):
    if type(response) == str and response[:5] == 'Error':
        return True
    else:
        return False


def retry(response, url, QS):
    # Check for errors and retry up to 3 times
    retry_limit = 3
    while errors(response) is True and retry_limit > 0:
        # Log  warning with remaining number of retries
        logger.warning(
            'Error recieved retrying {} times'.format(retry_limit))
        # Log error with time, error, and URL
        logger.error("{} - {}".format(response[7:], url))
        print ('Error recieved retrying {} times'.format(retry_limit))
        # Retry the same query
        response = myget(url,QS)
        retry_limit -= 1
        # Exit after retrying 3 times
        if retry_limit == 0:
            logger.error('Maximum Retry Reached - {}'.format(url))
            sys.exit()


def query_api(url,QS):
    response = myget(url,QS)
    retry(response,url,QS)
    return response

def verbose(msg):
    if args['verbose'] is True: print(msg,'\n')
    
# get cmdline options
args=vars(getopts(sys.argv))
verbose('\n'.join(['Command line options, including defaults','\n'.join('{}={}'.format(key, val) for key, val in args.items())]))
# Read the config file to get settings
verbose('reading config file '+args['cfg_file'].name)
config = configparser.RawConfigParser()
config.read(args['cfg_file'].name)

# Read API key and strip whitespace
if args['api_key'] is None:
    api_key = config.get('Main', 'api_key')
    api_key = str.strip(api_key)
    verbose('API key from config file is {}'.format(api_key))
else:
    api_key=args['api_key']
    verbose('API key from config file, if any, overruled by command line')
# Read logging info
if args['log_file'] is None:
    log_file = config.get('Main', 'log_file')
    verbose('log file from config file is {}'.format(log_file))
else:
    log_file=args['log_file']
    verbose('log file from config file, if any, overruled by command line')

# Read hostName and strip whitepace
if args['server_name'] is None:
    hostName = config.get('Main', 'hostName')
    hostName = str.strip(hostName)
    verbose('host name from config file is {}'.format(hostName))
else:
    hostName=args['server_name']
    verbose('host name from config file, if any, overruled by command line')

##if feedName is spec'd, get the type, typepath, and feedpath
if args['feedName'] is not None:
    #get feed path and type
    feedType, feedPath = config.get('Feeds', args['feedName']).replace(' ','').split(',')

    #get feedTypePath
    feedTypePath=config.get('FeedTypePaths',feedType)

    verbose('for specified feed "{}"; feed type is {} and feed path is {}\n'.format(args['feedName'], feedType, feedPath))


#if option rtfm was specified, do that
if args['rtfm'] is True:
    verbose('--rtfm found on command line, getting and printing doc links from config file and exiting')
    if args['feedName'] is None:
            outtext=''
            doclinks=dict(config.items('FeedTypeDocs'))
            for doclink in doclinks:
                outtext=outtext+'\n{} feeds: https://{}/{}\n'.format(doclink, hostName, doclinks[doclink])
    else:
            doclink=config.get('FeedTypeDocs',feedType)
            outtext='https://{}/{}\n'.format(hostName, doclink) 
    print(outtext)
    exit()

# Configure logging
logFormat = '%(asctime)s: %(levelname)s: %(name)s: %(message)s'
datefmt = '%Y-%m-%m %H:%M:%S'
logging.basicConfig(filename=log_file,
                    level=logging.ERROR,
                    format=logFormat,
                    datefmt=datefmt)
logger = logging.getLogger(__name__)

##time stuff
#validate start and end times if given
#calculate start and end times if both not given
if args['before_time'] is None and args['after_time'] is None:
    now_time=(datetime.datetime.now())
    after_time=(now_time-datetime.timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    before_time=now_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    verbose('calculated default time window: {} to {}'.format(after_time, before_time))
#calculate one if only the other was given
elif args['before_time'] is None:
    #one was set, and it's not before_time
    #set before_time to 1 hr after after_time
    before_time=(after_time+datetime.timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    verbose('time window end set to one hour after specified after_time: {}'.format(before_time))
else:
    #one was set, and it was before_time
    #set after_time to 1 hr before before_time
    after_time=(before_time-datetime.timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")                              
    verbose('time window start set to one hour before specified before_time: {}'.format(after_time))
                                      
###make request string
##make query string out of parameters
QSitems={}
#api_key
QSitems['api_key'] = api_key
#after_time and before_time
QSitems['after'] = after_time
QSitems['before'] = before_time        
                                      
###make request
url = 'https://{}/{}{}'.format(hostName, feedTypePath, feedPath)
verbose(''.join(['URL to request: {}?'.format(url), '&'.join('{}={}'.format(key, val) for key, val in QSitems.items())]))
if args['experiment'] is True:  print('Request not submitted because -e or --experiment was specified on the command line')
else: print (query_api(url,QSitems))

