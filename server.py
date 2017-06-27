
from twisted.internet import reactor
from twisted.web import http
import json

class MyRequestHandler(http.Request):

    def process(self):
         self.setHeader('Content-Type','application/json')
         if 'name' in args:
             print(name)
         if 'age'in args:
             prin
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

reactor.listenTCP(8000,MyHTTPFactory())
reactor.run()