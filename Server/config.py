'''config.py - Create configurations here.'''
class BaseConfig( object ):

    HOST = '0.0.0.0'
    PORT = 6900
    ROOMS = [ 'General', 'Help', 'Programming' ]
    ENCODING = 'utf-8'
    BUFSZ = 4096
    BACKLOG = 5

    def __init__( self ):
        object.__init__( self )
