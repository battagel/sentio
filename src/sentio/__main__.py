"""
Entry point for the Sentio application
"""
from wsgiref.simple_server import make_server

from .api import router

if __name__ == '__main__':
    httpd = make_server('', 8000, router)
    httpd.serve_forever()
