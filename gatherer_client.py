#!/usr/bin/env python3
# This file extends the client in lib.network.client
from lib.network.distributed_client import Client
from configparser     import SafeConfigParser
from lib.card.card    import Card
from urllib.request   import Request
from urllib.request   import urlopen
from urllib.request   import HTTPError
import socket
import time
import json
import re


class GathererClient(Client):
    __failstrs__ = ["2cb5f52b7de8f981bbe74c8b81faf7a4"]
    __tmplate__ = "http://gatherer.wizards.com/Pages/Card/Details.aspx?multiverseid=%i"
    __rsp__ = 'OK'

    def __init__(self, *args, **kwargs):
        Client.__init__(self, *args, **kwargs)
        self.__delay__ = 5
        self.__has_deck__ = False
        self.__data__ = b''
        self.__d_id__ = 0
        self.__sleep_flag__ = False

    def upkeep(self):
        if not self.__has_deck__:
            self.__conn__.send("NEXT".encode())
        else:
            self.__conn__.send(("OKAY %i" % len(self.__data__)).encode())

    def handle(self, m):
        m = m.split(' ', 1)

        if m[0] == 'PAGEID':
            self.__d_id__ = int(m[1])
            text = ""
            try:
                text = str(urlopen(Request((self.__tmplate__ % self.__d_id__))
                                           ).read(), "utf-8")
                print("GOT CARD %i" % (self.__d_id__))
                text = re.sub(r'\xe2', '-', text)
#                print(text)
                c = Card(None)
                c.loadFromGatherer(text)
                print(c.export())
                self.__data__ = json.dumps(c.export()).encode()
                self.__has_deck__ = True

            except HTTPError:
                self.__conn__.send(("FAIL %i" % self.__d_id__).encode())
                print("FAILED CARD ID %i, REDIRECT" % self.__d_id__)
                return

            except RuntimeError as e:
                msg = "FAILED TO PARSE DECK, '%s'" % str(e)
                self.__conn__.send(("FAIL %i %s" % (self.__d_id__,
                                                    msg).encode()))
                print(msg)
                return

            except Exception as e:
                print(e)
                self.__conn__.send(("FATAL %s" % str(e)).encode())
                self.__conn__.close()
                self.join()

        elif m[0] == 'GOAHEAD':
            print("GOT GOAHEAD SIGNAL")
            print(self.__data__)
            self.__conn__.send(self.__data__)

        elif m[0] == '1':
            print("UPLOADED CARD %7i" % (self.__d_id__))
            self.__has_deck__ = False
            self.__sleep_flag__ = True

        elif m[0] == '0':
            print("ERROR UPLOADING DECK %i CONTINUING...." % self.__d_id__)

        elif m[0] == 'RECONNECT':
            HOST, PORT = self.__conn__.getpeername(), 9001
            self.__conn__.close()
            time.sleep(int(m[1]))
            self.__conn__ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__conn__.bind((HOST, PORT))

        elif m[0] == 'DONE':
            print("RECIEVED DONE SIGNAL FROM SERVER")
            self.__conn__.close()
            self.join()

        if(self.__sleep_flag__):
            time.sleep(self.__delay__)
            self.__sleep_flag__ = False

if __name__ == "__main__" or 1:
    parser = SafeConfigParser()
    parser.read('/u/reid/OpenSourcerer/settings.ini')

    client = GathererClient(parser.get('scrape', 'master'),
                            int(parser.get('scrape', 'port')),
                           )
    client.daemon = False
    client.run()

