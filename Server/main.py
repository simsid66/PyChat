'''run.py - use this to run the server.'''

from config import BaseConfig
from server import Server

if __name__ == '__main__':

    cfg = BaseConfig()

    server = Server( cfg )

    server.run()
