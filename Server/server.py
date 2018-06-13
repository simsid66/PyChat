'''server.py - The main hosting classes.'''

import socket, sys, select

from config import BaseConfig
from client import Client

#Server object - main control over everything.
class Server( object ):
    def __init__( self, config:BaseConfig or None ):
        object.__init__(self)

        self.__sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.__host = config.HOST or '127.0.0.1'
        self.__port = config.PORT or 6900

        self.CLIENT_SOCKS = [ self.__sock ]
        self.CLIENTS = []
        self.NICKS = []
        self.ROOMS = config.ROOMS or [ 'General', 'Help', 'Programming' ]
        self.CONFIG = config

    def run( self ):

        sys.stderr.write( '[SOCKET] Attempting to bind server socket to %s:%d...\r\n' % ( self.__host, self.__port ) )
        sys.stderr.flush()

        try:
            self.__sock.bind( ( self.__host, self.__port ) )

        except socket.error:

            sys.stderr.write( '[ERROR] Could not bind socket to %s:%d.\r\n' % ( self.__host, self.__port ) )
            sys.stderr.flush()

            sys.exit()

        self.__sock.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )

        sys.stderr.write( '[SOCKET] Server is now up and running!\r\n' )
        sys.stderr.flush()

        self.__sock.listen( 5 )

        while True:

            read, write, err = select.select( self.CLIENT_SOCKS, [], [] )

            for sock in read:
                if sock == self.__sock:

                    client,addr = self.__sock.accept()

                    sys.stderr.write( '[SOCKET] %s:%d connected.\r\n' % addr )
                    sys.stderr.flush()

                    self.CLIENT_SOCKS.append( client )

                    obj = Client( self, client )

                    self.CLIENTS.append( obj )

                else:

                    match = False
                    
                    for i in self.CLIENTS:
                        if i.sock == sock:
                            
                            match = True
                            i.recv()
                            
                            break

                    if not match:

                        sock.close()

                        self.CLIENT_SOCKS.remove( sock )
                        
        
