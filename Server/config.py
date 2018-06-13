'''config.py - Create configurations here.'''
from room import Room

class BaseConfig( object ):

    HOST = '127.0.0.1'
    PORT = 6900
    ROOMS = [ Room( 'General' ), Room( 'Help' ), Room( 'Programming' ) ]
    ENCODING = 'utf-8'
    START_ROOMS = [ Room( 'Help' ) ]
    BUFSZ = 4096

    def __init__( self ):
        object.__init__( self )
