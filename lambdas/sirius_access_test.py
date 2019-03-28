import includes
import os
import json
import requests
import urllib3
import pprint
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def test_handler(event, context):
    if 'URL_MEMBRANE' not in os.environ:
        print('URL_MEMBRANE not set')
        exit(1)

    membrane_url = os.environ['URL_MEMBRANE']

    print('Membrane URL:' + membrane_url)

    url = membrane_url + '/auth/sessions'

    print('Auth URL: ' + url)

    r = requests.get(membrane_url + '/healthcheck.php', verify=False, headers={'host': 'membrane'})

    if r.status_code == 200:
        print('Appears we can talk to membrane')
    else:
        print('Unable to access membrane')
        pprint.pprint(r.text)
        exit(2)

    if 'CREDENTIALS' not in os.environ:
        print('CREDENTIALS not set, stopping here')
        exit(3)

    print('Attempting to login')

    data = {'user': json.loads(os.environ['CREDENTIALS'])}

    r = requests.post(url, json=data, verify=False, headers={'host': 'membrane'})

    if r.status_code == 201:
        print('Login successful')
    else:
        print('Login failed')
        pprint.pprint(r.text)
