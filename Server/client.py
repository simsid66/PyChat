'''client.py - holds the enums and classes needed for PyChat's user system.'''
import socket, sys

#Enumeration of the client's current state.
class ClientState:

    DISCONNECTED = 0
    SETNICK = 1
    CHATTING = 2

#Client object. Server uses this as an interface to communicate with clients.
class Client( object ):
    def __init__( self, server, sock:socket.socket, config = None ):
        object.__init__( self )
        
        self.__sock = sock
        self.sock = self.__sock

        peername = sock.getpeername()

        self.__host = peername[0]
        self.__port = peername[1]

        self.server = server
        self.config = server.CONFIG or config
        self.nick = 'Guest_%d' % len( self.server.CLIENT_SOCKS )
        self.state = ClientState.SETNICK
        self.rooms = []

    #Function to disconnect this client from the server.
    def disconnect( self ):

        self.__sock.close()

        sys.stderr.write( '[CLIENT] %s:%d (%s) disconnected.\n' % ( self.__host, self.__port, self.nick ) )
        sys.stderr.flush()

        #Leave each room.
        for room in self.rooms:

            room.clients.remove( self )
            room.servmsg( '%s has disconnected.\r\n' % self.nick )
            

        self.server.CLIENTS.remove( self )
        self.server.CLIENT_SOCKS.remove( self.__sock )

        #Put ourselves in a disconnected state for cleanup.
        self.state = ClientState.DISCONNECTED

    #Function to change nickname.
    def changeNick( self, nick:str ):

        #If the nick is already taken, do not allow it.
        if nick in self.server.NICKS:

            self.send( 'MSG [SERVER] Nickname %s has already been taken.\r\n' )

        else:
            #Let everyone in the chat rooms know that someone changed their nickname.
            for room in self.rooms:
                room.servmsg( '%s is now known as %s.\r\n' % ( self.nick, nick ) )

            self.send( 'MSG [SERVER] You are now known as %s.\r\n' % nick )

            if self.nick in self.server.NICKS:
                    self.server.NICKS.remove( self.nick )
            self.nick = nick
            self.server.NICKS.append( nick )

            #Since users use the NICK command to join the server, change their user state to chatting if they just connected.
            if self.state == ClientState.SETNICK:
                self.state = ClientState.CHATTING

    #Function that allows the client to join a room.
    def joinRoom( self, room:str ):

        if self.state == ClientState.CHATTING:

            match = False

            #Make sure that the room exists.
            for i in self.server.ROOMS:
                if i.name.lower() == room.lower():

                    match = True
                    
                    #Only add client to list if they are not already in the channel.
                    if not self.nick in i.listnames():
                        i.servmsg( '%s has joined the room.\r\n' % self.nick )
                        self.send( 'MSG [SERVER] You have joined room %s.\r\n' % room )

                        i.clients.append( self )
                        self.rooms.append( i )
                    else:
                        self.send( 'MSG [SERVER] You are already in room %s.\r\n' % room )
                    break

            if not match:

                self.send( 'MSG [SERVER] Room %s does not exist on this server.\r\n' % room )

        else:
            self.send( 'MSG [SERVER] You must choose a nick using your clients nick command before joining a room.\r\n' )

    #Function that allows the client to leave a room.
    def leaveRoom( self, room:str ):

        match = False

        #Make sure that the room exists.
        for i in self.server.ROOMS:
            if i.name.lower() == room.lower():

                match = True

                if self.nick in i.listnames():
                    i.servmsg( '%s has left the room.\r\n' % self.nick )
                    self.send( 'MSG [SERVER] You have left the room %s.\r\n' )

                    i.clients.remove( self )
                    self.rooms.remove( i )
                else:
                    self.send( 'MSG [SERVER] You are not in room %s.\r\n' % room )

                break

        if not match:

            self.send( 'MSG [SERVER] Room %s does not exist on this server.\r\n' % room )

    #Function to send a message to a room.
    def chat( self, room:str, msg:str ):

        if self.state == ClientState.CHATTING:

            match = False

            #Make sure user is in room.
            for i in self.rooms:
                if i.name.lower() == room.lower():

                    match = True

                    i.clientmsg( self.nick, msg )

                    break

            if not match:

                self.send( 'MSG [SERVER] You are not in room %s.\r\n' % room )

        else:
            self.send( 'MSG [SERVER] You must choose a nick using your clients nick command before sending a message.\r\n' )
        
    #Function to recieve data from the client.
    def recv( self ):

        try:

            data = self.__sock.recv( self.config.BUFSZ or 4096 )

            #They probably disconnected if no data came through.
            if not data:

                self.disconnect()
                
            else:

                parseData( self, data )

        except socket.error:

            self.disconnect()

    #Sends data from the server to the client.
    def send( self, data:str ):

        send_data = data.encode( self.config.ENCODING or 'utf-8' )

        try:

            self.__sock.send( send_data )

        #If we cannot send, the client has disconnected or an error occured.
        except socket.error:

            self.disconnect()

#Takes client data and parses it to decide what to do.
def parseData( client:Client, data:bytes ):
    server = client.server

    recv_data = data.decode( client.config.ENCODING or 'utf-8' )
    recv_data = recv_data.rstrip()

    cmd = recv_data.split( ' ', 1 )[0]

    #Client sent exit command.
    if cmd == 'BYE' or cmd == 'EXIT':
        
        client.disconnect()

    #Client wants to change or set their nick.
    elif cmd == 'NICK':

        if len( recv_data.split() ) < 2:
            return

        nick = recv_data.split( ' ' )[1] or client.nick

        client.changeNick( nick )

    #Client wants to join a room.
    elif cmd == 'JOIN':

        if len( recv_data.split() ) < 2:
            return

        roomName = recv_data.split( ' ' )[1] or None

        if roomName == None:
            client.send( 'MSG [SERVER] Room name not specified.\r\n' )
        else:
            client.joinRoom( roomName )

    #Client wants to leave a room.
    elif cmd == 'LEAVE' or cmd == 'PART':

        if len( recv_data.split() ) < 2:
            return

        roomName = recv_data.split( ' ' )[1] or None

        if roomName == None:
            client.send( 'MSG [SERVER] Room name not specified.\r\n' )
        else:
            client.leaveRoom( roomName )

    #Client wants to say something.
    elif cmd == 'MSG':

        if len( recv_data.split() ) < 3:
            return

        roomName = recv_data.split( ' ' )[1]
        i = recv_data.index( roomName ) + len( roomName ) + 1
        msg = recv_data[i:]

        if len( msg ) < 1:
            return
        else:
            client.chat( roomName, msg )
