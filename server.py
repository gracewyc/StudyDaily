from twisted.web import server, resource
from twisted.internet import reactor
import os

# multi part encoding example: http://marianoiglesias.com.ar/python/file-uploading-with-multi-part-encoding-using-twisted/
class Simple(resource.Resource):
    isLeaf = True
    def render_GET(self, request):
        return "{0}".format(request.args.keys())
    def render_POST(self, request):
        print("in render_POST")
        print("name = ",request.args['filename'][0])
        print("age = ",request.args['age'][0])
        request.setHeader('Content-Length', os.stat('source.pdf').st_size)
        with open('source.pdf', 'rb') as fd:
            request.write(fd.read())
        request.finish()
        return server.NOT_DONE_YET

site = server.Site(Simple())
reactor.listenTCP(8080, site)
reactor.run()