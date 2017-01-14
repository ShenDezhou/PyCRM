#!/usr/bin/python
from gevent.wsgi import WSGIServer
from app import app

if __name__ == '__main__':
    # app.run('0.0.0.0')

    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()

