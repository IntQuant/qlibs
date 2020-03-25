"""
  Host multiplexer server for other examples
  Server is universal, but you will need to restart it for different examples
"""
from qlibs.net.multiplexer import MultiplexServer
MultiplexServer().serve_forever()