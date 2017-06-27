'''
from twisted.internet import reactor
from twisted.web import http
import json

class MyRequestHandler(http.Request):

    def process(self):
         self.setHeader('Content-Type','application/json')

         if self.resources.has_key(self.path):
             self.write(self.resources[self.path])
         else:
             self.setResponseCode(http.NOT_FOUND)
             self.write("<h1>Not Found</h1>Sorry, no such source")
         self.finish()
 
class MyHTTP(http.HTTPChannel):
     requestFactory=MyRequestHandler
 
class MyHTTPFactory(http.HTTPFactory):
     def buildProtocol(self,addr):
         return MyHTTP()

if __name__ == '__main__':
   cf = MyHTTP()
   reactor.connectTCP('127.0.0.1', 8000, cf)
   reactor.run()
'''


#!/usr/bin/env python
# Copyright (c) 2014, Peter Ruibal.  All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
from twisted.internet import protocol, reactor
from twisted.internet.error import CannotListenError, ConnectError
from twisted.internet.interfaces import IReactorTCP, IReactorSSL
from twisted.protocols import tls
from twisted.python import log
from twisted.web import http
from zope.interface import implements


class ProxyConnectError(ConnectError):
    pass


class HTTPProxiedClientFactory(protocol.ClientFactory):
    """ClientFactory wrapper that triggers an HTTP proxy CONNECT on connect"""
    '''
    def __init__(self, delegate, dst_host, dst_port):
        self.delegate = delegate
        self.dst_host = dst_host
        self.dst_port = dst_port
    '''
    '''
    def startedConnecting(self, connector):
        return self.delegate.startedConnecting(connector)
    '''
   
    '''
    def buildProtocol(self, addr):
        p = HTTPConnectTunneler()
        p.factory = self
        return p
    '''
    protocol = HTTPConnectTunneler

    def clientConnectionFailed(self, connector, reason):
        #return self.delegate.clientConnectionFailed(connector, reason)
        print("clientConnectionFailed");
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        #return self.delegate.clientConnectionLost(connector, reason)
        print("clientConnectionLost");
        reactor.stop()


class HTTPConnectTunneler(protocol.Protocol):
 
    http = None
    otherConn = None
    noisy = True
    
    '''
    def __init__(self, host, port, orig_addr):
        self.host = host
        self.port = port
        self.orig_addr = orig_addr
    '''

    def connectionMade(self):
        self.http = HTTPConnectSetup(self.host, self.port)
        self.http.parent = self
        self.http.makeConnection(self.transport)

    def connectionLost(self, reason):
        if self.noisy:
            log.msg("HTTPConnectTunneler connectionLost", reason)

        if self.otherConn is not None:
            self.otherConn.connectionLost(reason)
        if self.http is not None:
            self.http.connectionLost(reason)

    def proxyConnected(self):
        # TODO: Bail if `self.factory` is unassigned or
        # does not have a `delegate`
        self.otherConn = self.factory.delegate.buildProtocol(self.orig_addr)
        self.otherConn.makeConnection(self.transport)

        # Get any pending data from the http buf and forward it to otherConn
        buf = self.http.clearLineBuffer()
        if buf:
            self.otherConn.dataReceived(buf)

    def dataReceived(self, data):
        if self.otherConn is not None:
            if self.noisy:
                log.msg("%d bytes for otherConn %s" %
                        (len(data), self.otherConn))
            return self.otherConn.dataReceived(data)
        elif self.http is not None:
            if self.noisy:
                log.msg("%d bytes for proxy %s" %
                        (len(data), self.otherConn))
            return self.http.dataReceived(data)
        else:
            raise Exception("No handler for received data... :(")


class HTTPConnectSetup(http.HTTPClient):
    """HTTPClient protocol to send a CONNECT message for proxies.
    `parent` MUST be assigned to an HTTPConnectTunneler instance, or have a
    `proxyConnected` method that will be invoked post-CONNECT (http request)
    """
    noisy = True

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def connectionMade(self):
        self.sendCommand('CONNECT', '%s:%d' % (self.host, self.port))
        self.endHeaders()

    def handleStatus(self, version, status, message):
        if self.noisy:
            log.msg("Got Status :: %s %s %s" % (status, message, version))
        if str(status) != "200":
            raise ProxyConnectError("Unexpected status on CONNECT: %s" % status)

    def handleHeader(self, key, val):
        if self.noisy:
            log.msg("Got Header :: %s: %s" % (key, val))

    def handleEndHeaders(self):
        if self.noisy:
            log.msg("End Headers")
        # TODO: Make sure parent is assigned, and has a proxyConnected callback
        self.parent.proxyConnected()

    def handleResponse(self, body):
        if self.noisy:
            log.msg("Got Response :: %s" % (body))


if __name__ == '__main__':
    cf = HTTPProxiedClientFactory()
    reactor.connectTCP('127.0.0.1', 8000, cf)
    reactor.run()

