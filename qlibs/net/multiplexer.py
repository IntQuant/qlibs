from .asyncsocket import *
import socket
import struct
from threading import Lock, Thread
import time

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
        self.player_id = player_id
        self.data = data
    def __repr__(self):
        return f"PayloadEvent({self.player_id}, {self.data})"


class ReadyEvent:
    name = "ready"
    def __init__(self, timedelta):
        self.timedelta = timedelta


def convert_event(event):
    if event.name == "ready":
        return base_struct.pack(1, 0, 0, event.timedelta)
    elif event.name == "payload":
        return base_struct.pack(2, event.player_id, 0, 0) + event.data
    elif event.name == "playerjoined":
        return base_struct.pack(3, event.player_id, 0, 0)
    elif event.name == "playerleft":
        return base_struct.pack(4, event.player_id, 0, 0)
    else:
        raise ValueError("Unknown event %s" % event)


class MultiplexServer:
    def __init__(self, host="0.0.0.0", port=55126):
        sock = socket.socket()
        sock.bind((host, port))
        sock.listen()
        #server_socket = AsyncSocket(sock)
        self.socket_selector = ServerSelector(sock, self.on_connect, self.on_read)
        self.events = []
        self.passed_events = []
        self.current_player_id = -1
        self.fd_to_id = dict()
        self.step = 0
        self.ready_players = set()
        self.players = 0
        self.run_thread = True
        self.last_ready = time.monotonic()

    def on_connect(self, sock, addr):
        print("Connection from", addr)
        self.current_player_id += 1
        self.fd_to_id[sock.fileno()] = self.current_player_id
        sock = PacketSocket(sock, bytes_packet_reciever)
        data = base_struct.pack(0, self.current_player_id, self.step, 0) #Hello packet
        sock.send(bytes_packet_sender(data))
        self.events.append(PlayerJoinedEvent(self.current_player_id))
        for event in self.passed_events:
            sock.send(bytes_packet_sender(convert_event(event)))
        self.players += 1
        print("Done, currently", self.players, "online")
        return sock
    
    def on_read(self, sock):
        player_id = self.fd_to_id[sock.fileno()]
        if sock.closed:
            self.socket_selector.unregister(sock)
            self.events.append(PlayerLeftEvent(player_id))
            self.players -= 1
            print("Player left")
            self.ready_players.discard(player_id)
            self.check_all_ready()
            return
        packets = sock.recv()
        for packet in packets:
            aux_data, payload = packet[:base_struct.size], packet[base_struct.size:]
            aux_data = base_struct.unpack(aux_data)
            if aux_data[0] == 1: #Ready
                self.ready_players.add(player_id)
                self.check_all_ready()
            elif aux_data[0] == 2: #Data
                self.events.append(PayloadEvent(player_id, payload))
    
    def check_all_ready(self):
        if len(self.ready_players) == self.players:
            self.all_ready()
    
    def all_ready(self):
        curr = time.monotonic()
        self.events.append(ReadyEvent(curr-self.last_ready))
        self.last_ready = curr
        for event in self.events:
            self.passed_events.append(event) #TODO: Send events when they are recieved
            packet = bytes_packet_sender(convert_event(event))
            for sock in self.socket_selector.socket_iterator:
                sock.send(packet)
        self.events.clear()

    def serve_forever(self):
        while self.run_thread:
            self.socket_selector.select()
    
    def serve_in_thread(self):
        self._thread = Thread(target=self.serve_forever, daemon=True, name="multiplexer server")
        self._thread.start()

class MultiplexClient:
    def __init__(self, engine, host="localhost", port=55126):
        #Engine should be a class with step method, accepting float(deltatime) and list of events
        #Also it can have state property
        sock = socket.socket()
        sock.connect((host, port))
        self.socket = PacketSocket(sock, bytes_packet_reciever)
        self.engine = engine
        self.packets = list()
        self.player_id = None
        self.socket_lock = Lock()
        self.ready_to_step = True
        self.last_step = 0
        self.min_step_time = 0.5
        self.recv_packets()
        
    def recv_packets(self):
        #TODO timedelta recieving
        #TODO stop on lost connection
        packets = self.socket.recv()
        for packet in packets:
            aux_data, payload = packet[:base_struct.size], packet[base_struct.size:]
            aux_data = base_struct.unpack(aux_data)
            
            if aux_data[0] == 0:
                self.player_id = aux_data[1]
            elif aux_data[0] == 1: #Next step
                self.engine.step(aux_data[3], self.packets)
                self.packets.clear()
                self.ready_to_step = True
            elif aux_data[0] == 2:
                self.packets.append(PayloadEvent(aux_data[1], payload))
            elif aux_data[0] == 3:
                self.packets.append(PlayerJoinedEvent(aux_data[1]))
            elif aux_data[0] == 4:
                self.packets.append(PlayerLeftEvent(aux_data[1]))
    
    def step(self):
        if self.ready_to_step and time.time() - self.last_step > self.min_step_time:
            with self.socket_lock:
                self.last_step = time.time()
                self.socket.send(bytes_packet_sender(base_struct.pack(1, 0, 0, 0)))
        self.socket.send()
        self.recv_packets()
    
    def send_payload(self, data):
        with self.socket_lock:
            self.socket.send(bytes_packet_sender(base_struct.pack(2, 0, 0, 0)+data))

    def _eternal_runner(self):
        while self._shall_continue:
            self.step()
            time.sleep(0.01)

    def thread_runner(self):
        self._thread = Thread(target=self._eternal_runner)
        self._shall_continue = True
        self._thread.start()
    
    def stop_thread(self):
        self._shall_continue = False
        self._thread.join()
