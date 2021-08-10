import json
import requests
import urllib3
from requests.auth import HTTPBasicAuth


user='nagios'
personalApiToken='WgS9C14yZ9Z6amBv2g5Sdg'

baseURL = 'https://puppet4.akqa.net'
path='/api/v2/hosts?search=last_report>"70 minutes ago" and (status.failed > 0 or status.failed_restarts > 0) and status.enabled = true'


headers = {"Accept": "application/json,version=2", \
    "Content-Type": "application/json", 
    }


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def exit_msg_with_status(msg, status):
    print(msg)
    exit(status)

def getResponse(url, headers):
    response = requests.get(url, headers=headers, verify=False, auth=HTTPBasicAuth(user, personalApiToken))
    if response.status_code == requests.codes.ok:
        response = response.json()
        return response

    else: 
        exit_msg_with_status(f"Oops! Got {response.status_code} status.", 3)

def getFailedHosts(data):
    failedHost = []
    if data != '':
        for host in data["results"]:
            failedHost.append(host['certname'])
        return failedHost
    else: 
            exit_msg_with_status("An empty response was received.", 3)  


def main():

    json_response = getResponse(baseURL+path, headers)

    if json_response:
        if json_response['subtotal'] != '0':
            failed_hosts = getFailedHosts(json_response)
            exit_msg_with_status(f"Critical: Puppet run failed! Following hosts are in error state - {failed_hosts}", 2)

        else:
            exit_msg_with_status(f"OK: Nice! Everything seems to be running smooth.", 0)


if __name__ == '__main__':
    main()
