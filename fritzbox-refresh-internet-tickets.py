#!/usr/bin/env python3
"""fritz box refresh access profile tickets"""
from os import getenv
from sys import exit, stderr
import importlib
fritz = importlib.import_module("fritzbox-internet-tickets")

if __name__ == '__main__':
    password = getenv("FRITZBOX_PASSWORD")
    if password is not None:
        try:
            tickets = fritz.FritzBoxInternetTickets(
                host=getenv("FRITZBOX_HOST","fritz.box"),
                user=getenv("FRITZBOX_USERNAME",""),
                password=password
            ).refresh_internet_tickets()
            if tickets:
                print("\n".join(tickets))
            else:
                print("Could not find any Internet tickets.", file=stderr)
                exit(1)
        except Exception as e:
            print("ERROR: %s" % e, file=stderr)
            exit(1)
    else:
        print('Set FRITZBOX_USERNAME (if you have one), FRITZBOX_PASSWORD and FRITZBOX_HOST environment variables to configure.\nSet FRITZBOX_DEBUG environment variable for debug output.')
        exit(1)
