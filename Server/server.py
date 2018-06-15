'''server.py: PyChat server and room classes.'''

import socket, sys, select

from config import BaseConfig
from client import Client



class ChatRoom( object ):

    def __init__( self, name:str ):

        object.__init__( self )

        self.__name = name
        self.__users = []

    #Sends a user message to others in the room.

    def usermsg( self, msg:str, user:Client ):

        if not user in self.__users:

            user.send( 'MSG [SERVER] You are not in room %s.\r\n' % self.__name )

        else:

            #In case of lazy clients...
            
            if not msg.endswith( '\r\n' ):

                msg += '\r\n'

            #Broadcast the message to all clients.
                
            for usr in self.__users:

                usr.send( 'MSG %s %s %s' % ( self.__name, user.nick, msg ) )

            return 0

    #Sends a server message to users in the room.

    def servmsg( self, msg:str ):

        for user in self.__users:

            user.send( 'MSG %s [SERVER] %s\r\n' % ( self.__name, msg ) )

    #Gets the room name.

    def getName( self ):

        return str(self.__name)

    #Lists users in the room.

    def getUsers( self ):

        return list(self.__users)

    #Adds a user to the room.

    def addUser( self, user:Client ):

        #Make sure that we dont double-add a user.
        
        if user in self.__users:

            user.send( 'MSG [SERVER] You are already in room %s.\r\n' % self.__name ) 

        else:
            
            #Let everyone know that someone joined the room.
            
            self.servmsg( '%s has joined the room.'  % user.nick )

            self.__users.append( user )
            user.rooms.append( self )

            user.send( 'MSG [SERVER] You have joined %s.\r\n' % self.__name )
        
    #Removes a user from the room.
    
    def delUser( self, user:Client, disconnect = False ):

        #Make sure that the user is already in the room.

        if not user in self.__users:

            user.send( 'MSG [SERVER] You are not in room %s.\r\n' % self.__name )

        else:
            self.__users.remove( user )
            user.rooms.remove( self )

            #Let everyone know that someone is leaving the room.

            if disconnect:

                self.servmsg( "%s has disconnected." % user.nick )
                
            else:

                self.servmsg( '%s has left the room.' % user.nick )

                user.send( 'MSG [SERVER] You have left %s.\r\n' % self.__name )


class Server( object ):

    def __init__( self, config:BaseConfig ):

        self.__sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.__host = config.HOST
        self.__port = config.PORT
        self.__addr = ( config.HOST, config.PORT )

        self.CLIENT_SOCKS = [self.__sock]
        self.CLIENTS = []
        self.NICKS = []
        self.ROOMS = [ ChatRoom( name ) for name in config.ROOMS ]

        self.config = config

    def run( self ):

        sys.stderr.write( '[SERV] Starting up PyChat server...\r\n' )
        sys.stderr.flush()

        self.__sock.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )

        sys.stderr.write( '[SOCK] Attempting to bind server to %s:%d...' % self.__addr )
        sys.stderr.flush()

        try:
            self.__sock.bind( self.__addr )

        except socket.error:

            sys.stderr.write( 'FAIL\r\n' )
            sys.stderr.flush()

        sys.stderr.write( 'SUCCESS\r\n' )
        sys.stderr.write( '[SERV] Listening on %s:%d...\r\n' % self.__addr )

        self.__sock.listen( self.config.BACKLOG )

        while True:

            read, write, err = select.select( self.CLIENT_SOCKS, [], [] )

            for sock in read:

                if sock == self.__sock:

                    client, addr = self.__sock.accept()

                    sys.stderr.write( '[SOCK] New client! %s:%d.\r\n' % addr )

                    obj = Client( client, self )

                    self.CLIENT_SOCKS.append( client )
                    self.CLIENTS.append( obj )

                else:

                    for client in self.CLIENTS:

                        if client.sock == sock:

                            client.recv()

                            break

    def removeClient( self, client ):

        self.CLIENT_SOCKS.remove( client.sock )
        self.CLIENTS.remove( client )

    def listRoomNames( self ):

        rooms = []

        for i in self.ROOMS:

            name = i.getName()

            rooms.append( name.lower() )

        return rooms

    def getRoom( self, name:str ):

        for i in self.ROOMS:

            if i.getName().lower() == name.lower():

                return i
    
        
