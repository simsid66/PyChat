import socket, sys

class ClientState:

    AUTH = 0
    CHAT = 1


class Client( object ):

    def __init__( self, sock:socket.socket, server, config = None ):

        object.__init__( self )

        self.__sock = sock
        self.sock = sock

        peername = sock.getpeername()

        self.__addr = peername
        self.__host = peername[0]
        self.__port = peername[1]

        self.server = server
        self.config = server.config or config
        self.nick = 'Guest_%d' % len( self.server.CLIENT_SOCKS )
        self.state = ClientState.AUTH
        self.rooms = []

    def disconnect( self ):

        self.__sock.close()

        sys.stderr.write( '[CLIENT] %s:%d (%s) disconnected.\r\n' % ( self.__host, self.__port, self.nick ) )
        sys.stderr.flush()

        for room in self.rooms:

            room.delUser( self, True )

        self.server.removeClient( self )

    def joinRoom( self, name:str ):

        roomNames = self.server.listRoomNames()

        if name.lower() in roomNames:

            room = self.server.getRoom( name )

            room.addUser( self )

        else:

            self.send( 'MSG [SERVER] That room does not exist.\r\n' )

    def leaveRoom( self, name:str ):

        roomNames = self.server.listRoomNames()

        if name.lower() in roomNames:

            room = self.server.getRoom( name )

            room.delUser( self )

        else:


            self.send( 'MSG [SERVER] That room does not exist.\r\n' )

    def setNick( self, name:str ):

        if name in self.server.NICKS:

            self.send( 'MSG [SERVER] Nickname %s has already been taken!\r\n' % name )

        else:
            for room in self.rooms:

                room.servmsg( '%s is now known as %s.' % ( self.nick, name ) )

            if self.nick in self.server.NICKS:

                self.server.NICKS.remove( self.nick )
            
            self.server.NICKS.append( name )
            self.nick = name

            self.send( 'MSG [SERVER] You are now known as %s.\r\n' % self.nick )

            if self.state == ClientState.AUTH:

                self.state = ClientState.CHAT
                

    def chat( self, name:str, msg:str ):

        if self.state == ClientState.CHAT:

            roomNames = self.server.listRoomNames()

            if name.lower() in roomNames:

                room = self.server.getRoom( name )

                room.usermsg( msg, self )

            else:

                self.send( 'MSG [SERVER] That room does not exist.\r\n' )

        else:

            self.send( 'MSG [SERVER] You must choose a nickname before sending a message.\r\n' )

    def recv( self ):

        try:

            data = self.__sock.recv( self.config.BUFSZ )

            if not data:

                self.disconnect()

            else:

                Commands.parse( self, data )

        except socket.error:

            self.disconnect()

    def send( self, data:str ):

        send_data = data.encode( self.config.ENCODING )

        try:

            self.__sock.send( send_data )

        except socket.error:

            self.disconnect()


class Commands:

    cmds = {}
    params = {}

    def command( name:str, params = None ):

        def cmd_deco( func:callable ):

            Commands.cmds[name] = func

            if params is not None:

                Commands.params[name] = '%s %s' % ( name, params )

            else:

                Commands.params[name] = name

            return func

        return cmd_deco

    def parse( user:Client, data:bytes ):

        try:
            recv_data = data.decode( user.config.ENCODING )
            recv_data = recv_data.rstrip()
        except:
            return
        

        cmd = recv_data.split( ' ', 1 )[0].upper()

        if cmd in Commands.cmds.keys():

            Commands.cmds[cmd]( user, recv_data )

        else:

            user.send( 'MSG [SERVER] That command is not supported by this server.\r\n' )

@Commands.command( 'BYE', '( Disconnects you from the server. )' )
@Commands.command( 'EXIT', '( Disconnects you from the server. )' ) 
@Commands.command( 'DISCONNECT', '( Disconnects you from the server. )' )
def bye( user, data ):

    user.disconnect()


@Commands.command( 'HELP', '[command] ( Lists available commands or displays parameters for a command. )' )
@Commands.command( 'PARAMS', '[command] ( Lists available commands or displays parameters for a command. )' )
def params( user, data ):

    data = data.split( ' ' )

    if len( data ) < 2:

        msg = 'MSG [SERVER] Commands: (use HELP <command> for more info.)\r\n'

        for i in Commands.cmds.keys():

            msg += i + '\r\n'

        user.send( msg )

    else:

        if data[1] in Commands.cmds.keys():

            msg = 'MSG [SERVER] %s\r\n' % Commands.params[data[1]]

            user.send( msg )

        else:

            user.send( 'MSG [SERVER] Command not found.\r\n' )

@Commands.command( 'JOIN', '<Room Name> ( Adds you to a chat room on the server. )' )
def join( user, data ):

    data = data.split( ' ' )

    if len( data ) < 2:

        user.send( 'MSG [SERVER] Missing required parameter <Room Name>.\r\n' )

    else:

        user.joinRoom( data[1] )

@Commands.command( 'PART', '<Room Name> ( Removes you from a chat room on the server. )' )
@Commands.command( 'LEAVE', '<Room Name> ( Removes you from a chat room on the server. )' )
def part( user, data ):

    data = data.split( ' ' )

    if len( data ) < 2:

        user.send( 'MSG [SERVER] Missing required parameter <Room Name>.\r\n' )

    else:

        user.leaveRoom( data[1] )

@Commands.command( 'MSG', '<Room Name> <Message> ( Sends a message to a joined chat room non the server. )' )
def msg( user, data ):

    data = data.split( ' ', 2 )

    if len( data ) < 3 and len( data ) > 1:

        user.send( 'MSG [SERVER] Missing required parameter <Message>.\r\n' )

    elif len( data ) < 2:

        user.send( 'MSG [SERVER] Missing required parameter <Room Name>.\r\n' )

    else:

        user.chat( data[1], data[2] )

@Commands.command( 'NICK', '<Nickname> ( Sets your nickname. )' )
def nick( user, data ):

    data = data.split( ' ' )

    if len( data ) < 2:

        user.send( 'MSG [SERVER] Missing required parameter <Nickname>.\r\n' )

    else:

        user.setNick( data[1] )
            
