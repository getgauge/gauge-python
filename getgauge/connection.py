import os
import socket
import struct

from messages.messages_pb2 import Message


def connect():
    gauge_internal_port = os.environ['GAUGE_INTERNAL_PORT']
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", int(gauge_internal_port)))
    return s


def read_message(s):
    len_buf = _decode_varint(s)[0]
    msg_buf = _socket_read_n(s, len_buf)
    msg = Message()
    msg.ParseFromString(msg_buf)
    return msg


def send_message(response, msg, s):
    response.messageId = msg.messageId
    s_response = response.SerializeToString()
    _encode_varint(s.sendall, len(s_response))
    s.sendall(s_response)


def _decode_varint(in_file):
    result = 0
    shift = 0
    pos = 0
    mask = 0xffffffff
    while 1:
        c = in_file.recv(1)
        if len(c) == 0:
            return (0, 0)
        b = struct.unpack('<B', c)[0]
        result |= ((b & 0x7f) << shift)
        pos += 1
        if not (b & 0x80):
            if result > 0x7fffffffffffffff:
                result -= (1 << 64)
                result |= ~mask
            else:
                result &= mask
                return (result, pos)
        shift += 7
        if shift >= 64:
            raise IOError('Too many bytes when decoding varint.')
    return result


local_chr = chr


def _encode_varint(write, value):
    bits = value & 0x7f
    value >>= 7
    while value:
        write(local_chr(0x80 | bits))
        bits = value & 0x7f
        value >>= 7
    return write(local_chr(bits))


def _socket_read_n(sock, n):
    buf = ''
    while n > 0:
        data = sock.recv(n)
        if data == '':
            raise RuntimeError('unexpected connection close')
        buf += data
        n -= len(data)
    return buf
