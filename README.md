# win-acme-pdns plugin

Plugin for WIN-ACME (https://www.win-acme.com/) DNS validation using (self-hosted) PowerDNS server with web API.

## Usage
Install script somewhere on server. You can use pyinstaller to pack script to exe file so it can be used on machines without installed python.

In Windows environment variables define these 3 variables:
* WINACME_PDNS_URL - URL address of PowerDNS web API
* WINACME_PDNS_SERVERID - Server ID in web API, usually localhost
* WINACME_PDNS_TOKEN - authentication token for web API

In win-acme, ask for new certificate. For validation select dns-01 own script and type path of this script. Script accepts default parameters suggested by win-acme, specifically for creation:

``
create {Identifier} {RecordName} {Token}
``

and for record delete:

``
delete {Identifier} {RecordName} {Token}
``