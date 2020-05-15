# Written by S. Mevawala, modified by D. Gitzel

import logging
import socket

import channelsimulator
import utils
import sys

class Sender(object):

    def __init__(self, inbound_port=50006, outbound_port=50005, timeout=10, debug_level=logging.INFO):
        self.logger = utils.Logger(self.__class__.__name__, debug_level)

        self.inbound_port = inbound_port
        self.outbound_port = outbound_port
        self.simulator = channelsimulator.ChannelSimulator(inbound_port=inbound_port, outbound_port=outbound_port,
                                                           debug_level=1)
        self.simulator.sndr_setup(timeout)
        self.simulator.rcvr_setup(timeout)

    def send(self, data):
        raise NotImplementedError("The base API class has no implementation. Please override and add your own.")


class BogoSender(Sender):

    def __init__(self):
        super(BogoSender, self).__init__()

    def send(self, data):
        self.logger.info("Sending on port: {} and waiting for ACK on port: {}".format(self.outbound_port, self.inbound_port))
        while True:
            try:
                self.simulator.u_send(data)  # send data
                ack = self.simulator.u_receive()  # receive ACK
                self.logger.info("Got ACK from socket: {}".format(
                    ack.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
                break
            except socket.timeout:
                pass


def checksum(data):
	'''
	computes checksum of the array
	:param data: data to compute checksum on
	:return result: value of checksum
	'''
	result = 0
	# Checksum computed by adding byte after byte and modulo 255 to keep it in one byte
	for i in data:
		result = result + i
		result = result % 255
	return result


def make_frame(data):
	previous_packet_num = -1
	next_packet_num = 0
	array = bytearray(1024)
	array[0] = checksum(data)
	array[1] = next_packet_num
	previous_packet_num = previous_packet_num + 1
	next_packet_num = next_packet_num + 1
	if next_packet_num > 255:
		next_packet_num = 0
	if previous_packet_num > 255:
		previous_packet_num = 0
	array[2:1023] = data
	return array


class ReliableSender(Sender):
	def __init__(self):
		super(ReliableSender, self).__init__()

	def send(self, data):
		self.logger.info("Sending on port: {} and waiting for ACK on port: {}".format(self.outbound_port, self.inbound_port))
		#print "Sending on port: {} and waiting for ACK on port: {}".format(self.outbound_port, self.inbound_port)
		frame = make_frame(data)
		self.send_frame(frame)


	def send_frame(self, frame):
		while True:
			try:
				self.simulator.u_send(frame)  # send data
				#print 'sent'
				self.simulator.u_send(frame)
				self.simulator.u_send(frame)
				self.simulator.u_send(frame)
				print "Sent frame, cheksum num = {}, number = {}\n".format(frame[0], frame[1])
				self.logger.info("Send data: {} 3 times".format(frame[2:1023]))
		        	ack = self.simulator.u_receive()  # receive ACK
        			self.logger.info("Got ACK from socket: {}".format(
					ack.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
				break
			except socket.timeout:
				pass




if __name__ == "__main__":
    # test out BogoSender
    DATA = bytearray(sys.stdin.read())
    sndr = ReliableSender()
    sndr.send(DATA)
