#!/usr/bin/env python3
"""fritz box api calls for python"""
import requests
from hashlib import md5
from os import getenv
import xml.etree.ElementTree as ET
import re
import logging

# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig(format='%(levelname)s: %(message)s')
logging.getLogger().setLevel(logging.DEBUG if getenv("FRITZBOX_DEBUG") else logging.ERROR)
requests_log = logging.getLogger("requests.packages.urllib3")
#requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

class FritzBoxInternetTickets(object):
    """class for interaction with the FRITZ!Box(R)"""

    def __init__(self, host='fritz.box', user='', password=''):
        self.host = 'http://' + host
        self.password = password
        self.user = user
        self.sid = self._get_sid()

    def _get_sid(self):
        """
        gets a sesion id

        see [1] for details

        [1] http://www.avm.de/de/Extern/files/session_id/AVM_Technical_Note_-_Session_ID.pdf
        """
        response = requests.get('{}/login_sid.lua'.format(self.host))
        tree = ET.fromstring(response.content)
        for one in tree.findall('Challenge'):
            challenge = one.text
        md5sum = md5((challenge + "-" + self.password).encode('utf-16LE'))
        md5sum = md5sum.hexdigest()
        challenge_response = challenge + '-' + md5sum
        response = requests.get(
            '{}/login_sid.lua?username={}&response={}'.format(
                self.host, self.user, challenge_response
            ),
        )
        # we are looking for something like this:
        # <SID>0123456789abcdef</SID>
        match = re.search(r'\<SID\>([^<]+)\</SID\>', response.text)
        if match:
            sid = match.groups()[0]
        if not sid or sid == "0000000000000000":
            logging.error('could not get sid, response was:\n%s' % response.text)
            raise Exception('could not get sid')
        return sid

    def get_internet_tickets(self):
        data_url = f"{self.host}/data.lua"
        response = requests.post(data_url, {
            "sid": self.sid,
            "lang": "de",
            "page": "kidPro"
        })
        logging.debug(response.text)
        tickets = re.findall(r'<td class="" id="Ticket-\d+">(\d+)<\/td>', response.text)

        logging.debug(tickets)
        return tickets

    def refresh_internet_tickets(self):
        data_url = f"{self.host}/data.lua"
        response = requests.post(data_url, {
            "sid": self.sid,
            "lang": "de",
            "page": "kidPro",
            "refresh": ""
        })
        logging.debug(response.text)
        return self.get_internet_tickets()
