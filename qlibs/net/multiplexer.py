from .asyncsocket import *
import socket
import struct
from threading import Lock, Thread
import time
import logging
logger = logging.getLogger("qlibs.net.multiplexer")

base_struct = struct.Struct("!iiid")

class PlayerJoinedEvent:
    name = "playerjoined"
    def __init__(self, player_id):
        self.player_id = player_id
    def __str__(self):
        return f"Player joined {self.player_id}"


class PlayerLeftEvent:
    name = "playerleft"
    def __init__(self, player_id):
        self.player_id = player_id
    def __str__(self):
        return f"Player left {self.player_id}"


class PayloadEvent:
    name = "payload"
    def __init__(self, player_id, data):
        if type(data) != bytes:
            raise ValueError("Data is not bytes")
        self.player_id = player_id
        self.data = data
    def __repr__(self):
        return f"PayloadEvent({self.player_id}, {self.data})"


class ReadyEvent:
    name = "ready"
    def __init__(self, timedelta):
        self.timedelta = timedelta


class ReconstructEvent:
    name = "reconstruct"
    def __init__(self, data):
        if type(data) != bytes:
            raise ValueError("Data is not bytes")
        self.data = data


class MultiplexerException(Exception): pass


def convert_event(event):
    if event.name == "ready":
        return base_struct.pack(1, 0, 0, event.timedelta)
    elif event.name == "payload":
        return base_struct.pack(2, event.player_id, 0, 0) + event.data
    elif event.name == "playerjoined":
        return base_struct.pack(3, event.player_id, 0, 0)
    elif event.name == "playerleft":
        return base_struct.pack(4, event.player_id, 0, 0)
    elif event.name == "reconstruct":
        return base_struct.pack(5, 0, 0, 0) + event.data
    else:
        raise ValueError("Unknown event %s" % event)


class MultiplexServer:
    """
    Server for multiplexer
    """
    def __init__(self, host="0.0.0.0", port=55126, engine_packer=None):
        sock = socket.socket()
        sock.bind((host, port))
        sock.listen()
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.socket_selector = ServerSelector(sock, self._on_connect, self._on_read)
        self.events = []
        self.passed_events = []
        self.current_player_id = -1
        self.fd_to_id = dict()
        self.step = 0
        self.ready_players = set()
        self.players = 0
        self.run_thread = True
        self.last_ready = time.monotonic()
        self.engine_packer = engine_packer
        self.state = None
        #if self.engine_packer is not None:
        #    self.state = self.engine_packer()
        self.time_between_selection = 0.001
        self.last_pack = time.monotonic()
        self.pack_delay = 2

    def _on_connect(self, sock, addr):
        logger.info("Connection from %s", addr)
        self.current_player_id += 1
        self.fd_to_id[sock.fileno()] = self.current_player_id
        sock = PacketSocket(sock, bytes_packet_reciever)
        data = base_struct.pack(0, self.current_player_id, self.step, 0) #Hello packet
        sock.send(bytes_packet_sender(data))
        if self.engine_packer is not None:
            if time.monotonic() - self.last_pack > self.pack_delay:
                self.state = self.engine_packer() or self.state
                self.passed_events.clear()
        if self.state is not None:
            self.last_pack = time.monotonic()
            pl = convert_event(ReconstructEvent(self.state))
            logger.debug("Sending reconstruct packet len %s", len(pl))
            sock.send(bytes_packet_sender(pl))
        self.events.append(PlayerJoinedEvent(self.current_player_id))
        for event in self.passed_events:
            sock.send(bytes_packet_sender(convert_event(event)))
        self.players += 1
        logger.info("Done, currently %s online", self.players)
        return sock
    
    def _on_read(self, sock):
        player_id = self.fd_to_id[sock.fileno()]
        packets = sock.recv()
        for packet in packets:
            aux_data, payload = packet[:base_struct.size], packet[base_struct.size:]
            aux_data = base_struct.unpack(aux_data)
            if aux_data[0] == 1: #Ready
                self.ready_players.add(player_id)
                self._check_all_ready()
            elif aux_data[0] == 2: #Data
                self.events.append(PayloadEvent(player_id, payload))
        if sock.closed:
            self.socket_selector.unregister(sock)
            self.events.append(PlayerLeftEvent(player_id))
            self.players -= 1
            logger.info("Player left")
            self.ready_players.discard(player_id)
            self._check_all_ready()
            return
    
    def _check_all_ready(self):
        if len(self.ready_players) == self.players:
            self._all_ready()
            self.ready_players.clear()
    
    def _all_ready(self):
        curr = time.monotonic()
        #logger.debug("All ready in %.2f ms", (curr-self.last_ready)*1000)
        self.events.append(ReadyEvent(curr-self.last_ready))
        self.last_ready = curr
        eventdata = b"".join(map(bytes_packet_sender, map(convert_event, self.events)))
        for event in self.events:
            self.passed_events.append(event) #TODO: Send events when they are recieved
        #    packet = bytes_packet_sender(convert_event(event))
        for sock in self.socket_selector.socket_iterator:
            sock.send(eventdata)
        self.events.clear()

    def serve_forever(self):
        while self.run_thread:
            self.socket_selector.select()
            time.sleep(self.time_between_selection)
    
    def serve_in_thread(self):
        self._thread = Thread(target=self.serve_forever, daemon=True, name="multiplexer server")
        self._thread.start()

    def stop_thread(self):
        self.run_thread = False

class MultiplexClient:
    """
    Client for multiplexer
    """
    def __init__(self, engine, engine_constructor=None, host="localhost", port=55126):
        #Engine should be a class with step method, accepting float(deltatime) and list of events
        sock = socket.socket()
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        sock.connect((host, port))
        self.pending_packets = []
        self.socket = PacketSocket(sock, bytes_packet_reciever)
        self.engine = engine
        self.engine_constructor = engine_constructor
        self.packets = list()
        self.player_id = None
        self.socket_lock = Lock()
        self.ready_to_step = True
        self.last_step = 0
        self.last_confirmed_step = 0
        self.min_step_time = 0.5
        self._recv_packets()
        
    def _recv_packets(self):
        packets = self.socket.recv()
        for packet in packets:
            aux_data, payload = packet[:base_struct.size], packet[base_struct.size:]
            try:
                aux_data = base_struct.unpack(aux_data)
            except struct.error as e:
                raise
            if aux_data[0] == 0:
                self.player_id = aux_data[1]
            elif aux_data[0] == 1: #Next step
                self.last_confirmed_step = time.monotonic()
                self.engine.step(aux_data[3], self.packets)
                self.packets.clear()
                self.ready_to_step = True
            elif aux_data[0] == 2:
                self.packets.append(PayloadEvent(aux_data[1], payload))
            elif aux_data[0] == 3:
                self.packets.append(PlayerJoinedEvent(aux_data[1]))
            elif aux_data[0] == 4:
                self.packets.append(PlayerLeftEvent(aux_data[1]))
            elif aux_data[0] == 5:
                if self.engine_constructor is None:
                    raise MultiplexerException("Server requested engine reconstruction but engine_constructor is None")
                logging.debug("Reconstructing engine")
                self.engine = self.engine_constructor(payload)
    
    def step(self):
        if self.ready_to_step and time.monotonic() - self.last_step > self.min_step_time:
            #logging.debug("Waiting for lock...")
            with self.socket_lock:
                #logging.debug("Performing step...")
                self.last_step = time.monotonic()
                self.pending_packets.append(bytes_packet_sender(base_struct.pack(1, 0, 0, 0)))
                data = b"".join(self.pending_packets)
                self.pending_packets.clear()
                self.socket.send(data)
                #logging.debug("Done!")
        with self.socket_lock:
            self.socket.send()
        self._recv_packets()
    
    def send_payload(self, data):
        with self.socket_lock:
            self.pending_packets.append(bytes_packet_sender(base_struct.pack(2, 0, 0, 0)+data))

    def _eternal_runner(self):
        while self._shall_continue:
            self.step()
            time.sleep(max(0, min(0.01, self.last_step + self.min_step_time - time.monotonic())))
            #time.sleep(0.1)
            if self.socket.reset:
                logger.warning("Socket is reset, stopping client")
                self._shall_continue = False

    def thread_runner(self):
        self._thread = Thread(target=self._eternal_runner, name="multiplex-client", daemon=True)
        self._shall_continue = True
        self._thread.start()
    
    def run_in_thread(self):
        self.thread_runner()

    def stop_thread(self):
        self._shall_continue = False
        self._thread.join()
