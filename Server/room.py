'''room.py - holds classes needed for PyChat's room system.'''

#Class for chat rooms, which are like walkie-talkie channels.
class Room( object ):

    def __init__( self, name:str ):
        object.__init__( self )

        self.name = name

        self.clients = []

    def servmsg( self, msg:str ):

        for client in self.clients:

            client.send( 'MSG [SERVER] %s' % msg )

    def clientmsg( self, nick:str, msg:str ):

        for client in self.clients:

            client.send( 'MSG %s %s' % ( nick, msg ) )

    def listnames( self ):

        names = []

        for i in self.clients:
            names.append( i.nick )

        return names
