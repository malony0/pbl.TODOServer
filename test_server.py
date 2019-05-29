from multiprocessing import Process
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from todoserver import PORT, API, V1, EVENT, StoppableServer, RequestHandler
import json

import os

URL = "http://localhost:"+str(PORT)+'/'+API+'/'+V1+'/'+EVENT

headers = {"Content-Type" : "application/json",}

## POST
def test_POST_valid():
    valid_data = {"deadline": "2019-06-11T14:00:00+09:00", "title": "レポート提出", "memo": ""}
    req = Request(URL, json.dumps(valid_data).encode(), headers)
    with urlopen(req) as res:
        body = json.load(res)
        assert res.getcode() == 200
        assert body["status"] == "success"
        assert body["message"] == "registered"

def test_POST_invalid():
    invalid_data = {"deadline": "2019/06/11T14:00:00", "title": "レポート提出", "memo": ""}
    req = Request(URL, json.dumps(invalid_data).encode(), headers)
    try:
        with urlopen(req) as res:
            body = res.read()
    except HTTPError as e:
        assert e.code == 400
        return
    except URLError as e:
        pass
    assert False

### GET

def test_GET():
    req = Request(URL)
    with urlopen(req) as res:
        print(res.read())



def f(name):
    with StoppableServer(('', PORT), RequestHandler) as server:
        server.serve_forever()

def main():
    p = Process(target=f, args=('bob',))
    p.start()

    req = Request(URL)
    with urlopen(req) as res:
        print(res.read())
    
    p.terminate()
    p.join()

#if __name__ == '__main__':
    #main()
    
