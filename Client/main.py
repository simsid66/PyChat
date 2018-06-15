import socket, sys

RECV_BUFSZ = 4096
CONN_TIMEOUT = 10 #Connection timeout time (in seconds)

class DataParser:

    cmds = {}

    def command( name:str ):

        def decorator( func:callable ):

            DataParser.cmds[name] = func

            return func

        return decorator

    def parse( data:str ):

        cmd = recv_data.split( ' ', 1 )[0].upper()

        if cmd in Commands.cmds.keys():

            Commands.cmds[cmd]( data )

class App:

    def __init__( self, host:str, port:int ):

        self.__host = host
        self.__port = port
        self.__addr = ( host, port )

        self.__sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )

        self.__sock.settimeout( CONN_TIMEOUT )

    def recv( self ):

        try:

            data = self.__sock.recv( RECV_BUFSZ )

            if data:

                DataParser.parse( data )

            else:

                self.__sock.close()

                sys.stdout.write( "[CLIENT] Disconnected from server.\r\n" )
                sys.stdout.flush()

                exit()

        except socket.error:

            self.__sock.close()

            sys.stdout.write( "[CLIENT] Disconnected from server.\r\n" )
            sys.stdout.flush()

            exit()

    def send( self ):

        msg = sys.stdin.readline().encode( 'utf-8' )

        try:
            self.__sock.send( msg )

        except socket.error:

            self.__sock.close()

            sys.stdout.write( "[CLIENT] Disconnected from server.\r\n" )
            sys.stdout.flush()

            exit()

            

            

@DataParser.command( 'MSG' )
def msg( data ):

    split = data.split( ' ' )

    if split[1] == '[SERVER]':

        data = data.split( ' ', 2 )

        sys.stdout.write( '%s: %s' % data[2:] )
        sys.stdout.flush()

                        

    
