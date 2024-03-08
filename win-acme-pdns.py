import sys
import requests
import json
import os


PDNS_URL = os.environ.get('WINACME_PDNS_URL', None)
PDNS_SERVER_ID = os.environ.get('WINACME_PDNS_SERVERID', None)
PDNS_TOKEN = os.environ.get('WINACME_PDNS_TOKEN', None)


def main():
    if not PDNS_URL or not PDNS_SERVER_ID or not PDNS_TOKEN:
        raise SystemExit('API URL, Server ID or Token was not specified in env variables')
    if len(sys.argv) != 5:
        raise SystemExit('Incorrect argument count')
    _, action, identifier, record_name, token = sys.argv
    if action == 'create':
        create_record(identifier, record_name, '"' + token + '"')
    elif action == 'delete':
        delete_record(identifier, record_name, '"' + token + '"')
    else:
        raise SystemExit('Unknown action')


def build_api_url(url_end):
    return PDNS_URL + '/api/v1/servers/' + PDNS_SERVER_ID + '/' + url_end


def build_api_headers():
    return {'X-API-Key': PDNS_TOKEN}


def find_zone(record_name):
    response = requests.get(build_api_url('zones'), headers=build_api_headers())
    if response.status_code != 200:
        raise SystemExit('Could not retrieve zones')
    pdns_domains = [_['name'].strip('.') for _ in response.json()]

    record_parts = record_name.strip('.').split('.')
    for _ in range(2, len(record_parts)):
        zone = '.'.join(record_parts[_::])
        if zone in pdns_domains:
            return zone
    raise SystemExit('No valid zone on PDNS server')


def create_rrset(record, *, delete=True, content=''):
    change_type = 'REPLACE'
    if delete:
        change_type = 'DELETE'
    records = []
    if not delete:
        records = [{'content': content, 'disabled': False}]
    rrset = {
        'name': record.strip('.') + '.',
        'type': 'TXT',
        'ttl': 1,
        'changetype': change_type,
        'records': records
    }
    return {'rrsets': [rrset]}


def notify_zone(zone):
    response = requests.put(build_api_url('zones/' + zone + './notify'), headers=build_api_headers())
    if response.status_code == 200:
        print('zone notified')


def create_record(identifier, record_name, token):
    pdns_zone = find_zone(record_name)
    rrset = json.dumps(create_rrset(record_name, delete=False, content=token))
    response = requests.patch(build_api_url('zones/' + pdns_zone), headers=build_api_headers(), data=rrset)
    if response.status_code == 204:
        print('Record created')
        notify_zone(pdns_zone)


def delete_record(identifier, record_name, token):
    pdns_zone = find_zone(record_name)
    rrset = json.dumps(create_rrset(record_name, delete=True))
    response = requests.patch(build_api_url('zones/' + pdns_zone), headers=build_api_headers(), data=rrset)
    if response.status_code == 204:
        print('Record deleted')
        notify_zone(pdns_zone)


if __name__ == '__main__':
    main()
