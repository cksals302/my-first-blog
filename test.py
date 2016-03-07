#!/usr/bin/python
#-*- coding: utf-8 -*-

# python 2.7.x
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import os
import re

PORT_NUMBER = 9080

# This class will handles any incoming request from
# the browser


class MyHandler(BaseHTTPRequestHandler):

    needProductSeqCase = {}
    needProductSeqCase['newUi-stats-productTrafficGraph'] = True

    EXTENSION_JSON = '.json'

    def _genParamDic(self, params):
        paramDic = {}
        for i in params.split('&'):
            if i.find('=') is -1:
                continue
            key, val = i.split('=')
            paramDic[key] = val
        return paramDic

    def _changeFileNameWithProductSeq(self, paramDic):

        jsonFileName = self.jsonFile[
            :self.jsonFile.find(MyHandler.EXTENSION_JSON)]
        productSeq = None
        if 'product_seq' in paramDic:
            productSeq = paramDic['product_seq']

        if (jsonFileName in MyHandler.needProductSeqCase) and productSeq != None:
            self.jsonFile = jsonFileName + '-' + productSeq + MyHandler.EXTENSION_JSON

        return self.jsonFile

    def _getStartEndOfRetMessage(self, reqType, paramDic):
        s = ''
        e = ''
        if reqType == 'jsonp' and paramDic is not None:
            s = paramDic['callback'] + '('
            e = ')'

        return s, e

    def _doSend(self, reqType, paramDic):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        # Open the static file requested and send it
        with open(os.curdir + os.sep + self.jsonFile) as f:
            start, end = self._getStartEndOfRetMessage(reqType, paramDic)

            retMessage = start
            retMessage += f.read()
            retMessage += end

            self.wfile.write(retMessage)

    # Handler for the GET requests
    def do_GET(self):

        # req url : http://localhost:9080/jsonp/page_name?callback=dsfd..&a=10

        EXTENSION_JSON = '.json'

        pathes = self.path.split('/')

        if len(pathes) < 3:
            return

        sep = re.split('/|\?', self.path)
        reqType = sep[1]
        jsonFileName = sep[2]

        self.jsonFile = jsonFileName + EXTENSION_JSON

        paramDic = None
        if len(sep) > 3:
            params = sep[3]
            paramDic = self._genParamDic(params)
            self._changeFileNameWithProductSeq(paramDic)

        self._doSend(reqType, paramDic)

        return

    # Handler for the POST requests
    def do_POST(self):

        # req url : http://localhost:9080/jsonp/page_name?callback=dsfd..&a=10
        self.do_GET()

        return


try:
    # Create a web server and define the handler to manage the
    # incoming request
    server = HTTPServer(('', PORT_NUMBER), MyHandler)
    print('Started httpserver on port ', PORT_NUMBER)

    # Wait forever for incoming htto requests
    server.serve_forever()

except KeyboardInterrupt:
    print('^C received, shutting down the web server')
    server.socket.close()
