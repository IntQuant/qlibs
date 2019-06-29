#TODO

class TCPLink():
    def __init__(self, connect_to=None, listen_on=None):
        assert (connect_to is not None) or (listen_on is not None)
        self.connect_to = connect_to
        self.listen_on = listen_on
        self.sockets = []
        self.listening_socket = None
        self.to_send = None
    def serve(self):
        pass
