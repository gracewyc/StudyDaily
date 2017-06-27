from twisted.internet import reactor
from twisted.web.client import Agent
from twisted.web.http_headers import Headers

from twisted.web.client import FileBodyProducer
from twisted.web.iweb import IBodyProducer
from twisted.web.test import test_newclient
from twisted.internet.defer import Deferred
from twisted.internet.protocol import Protocol
from pprint import pformat

import json

class BeginningPrinter(Protocol):
    def __init__(self, finished):
        self.finished = finished
        self.remaining = 1024 * 10

    def dataReceived(self, bytes):
        if self.remaining:
            display = bytes[:self.remaining]
            print 'Some data received:'
            print display
            self.remaining -= len(display)

    def connectionLost(self, reason):
        print 'Finished receiving body:', reason.getErrorMessage()
        self.finished.callback(None)

class SaveContents(Protocol):
    def __init__(self, finished, filesize, filename):
        print 'SaveContents'
        self.finished = finished
        self.remaining = filesize
        self.outfile = open(filename, 'wb')

    def dataReceived(self, bytes):
        if self.remaining:
            display = bytes[:self.remaining]
            self.outfile.write(display)
            self.remaining -= len(display)
        else:
            self.outfile.close()

    def connectionLost(self, reason):
        print 'Finished receiving body:', reason.getErrorMessage()
        self.outfile.close()
        self.finished.callback(None)

agent = Agent(reactor)
#f = open('source.pdf', 'rb')
data = {"name" : "foo", "age" : 42}
in_json = json.dumps(data)
print(in_json)
body = test_newclient.StringProducer("hello,world")
d = agent.request(
    'POST',
    'http://127.0.0.1:8080/',
    Headers({'User-Agent': ['Twisted Web Client Example'],
             'Content-Type': ['application/json']}),
    body)

def cbRequest(response):
    print 'Response version:', response.version
    print 'Response code:', response.code
    print 'Response phrase:', response.phrase
    print 'Response headers:'
    print 'Response length:', response.length
    print pformat(list(response.headers.getAllRawHeaders()))
    finished = Deferred()
    response.deliverBody(SaveContents(finished, response.length, 'test2.pdf'))
    return finished
d.addCallback(cbRequest)

def cbShutdown(ignored):
    reactor.stop()
d.addBoth(cbShutdown)

reactor.run()