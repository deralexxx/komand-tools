import configparser
import logging
import json
import ssl
import urllib.request
import urllib.parse
import argparse

logger = logging.getLogger('komand')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


config = configparser.ConfigParser()
config.read("config.cfg")

KOMAND_BASEURL = config.get('DEFAULT', 'KOMAND_BASEURL')
KOMAND_USERNAME = config.get('DEFAULT', 'KOMAND_USERNAME')
KOMAND_PASSWORD = config.get('DEFAULT', 'KOMAND_PASSWORD')


from requests.packages.urllib3 import disable_warnings
disable_warnings()  # TODO 2016-04-23 (RH) verify this



def getAuthToken():

    data2 = {"user_name": KOMAND_USERNAME,"user_secret":KOMAND_PASSWORD}
    request = urllib.request.Request(
        KOMAND_BASEURL+"/v2/sessions",
        data=bytes(json.dumps(data2), encoding="utf-8"))
    context = ssl._create_unverified_context()
    request.add_header('Accept', 'application/json')
    request.add_header('Content-type', 'application/json')
    request.get_method = lambda: 'POST'
    response = urllib.request.urlopen(request, context=context)
    data = json.loads(response.read().decode())
    logger.debug("token received: "+data.get("token"))

    return (data.get("token"))

def getWorkFlows(token=None):
    auth_header = "Bearer " + token

    context = ssl._create_unverified_context()

    request = urllib.request.Request(
        KOMAND_BASEURL+"/v2/workflows/")

    request.add_header('Authorization', auth_header)
    request.add_header('Accept', 'application/json')
    request.add_header('Content-type', 'application/json')
    request.get_method = lambda: 'GET'
    response = urllib.request.urlopen(request, context=context)

    # Hacky workaround for to large json data:
    import sys
    sys.setrecursionlimit(2500)

    response = response.read().decode()

    data = json.loads(response)
    for key in data["workflows"]:
        logger.debug(key.get("name")+" "+key.get("workflow_uid")) # you can switch that to print if you do not want to have the logger info in front

def getJobStatus(token=None,jobid=None):
    auth_header = "Bearer " + token

    logger.debug(jobid)
    context = ssl._create_unverified_context()

    data2 = {"jobid": jobid}

    request = urllib.request.Request(
        KOMAND_BASEURL+"/v2/jobs/"+jobid,
        data=bytes(json.dumps(data2), encoding="utf-8"))

    request.add_header('Authorization', auth_header)
    request.add_header('Accept', 'application/json')
    request.add_header('Content-type', 'application/json')
    request.get_method = lambda: 'GET'
    response = urllib.request.urlopen(request, context=context)
    data = json.loads(response.read().decode())

    logger.debug(data)

    logger.info("Job status: "+data.get("status"))

    logger.debug(KOMAND_BASEURL+"/jobs/details/" + data.get("job_id"))

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")
    parser.add_argument("-wm", "--workflow_map", help="show workflow map",
                        action="store_true")
    parser.add_argument("-j", "--job", help="show job status")

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.NOTSET)

    if args.workflow_map:
        auth_token = getAuthToken()
        getWorkFlows(auth_token)

    elif args.job:
        auth_token = getAuthToken()
        getJobStatus(auth_token,args.job)

