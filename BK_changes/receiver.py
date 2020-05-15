# Written by S. Mevawala, modified by D. Gitzel

import logging

import channelsimulator
import utils
import sys
import socket
from sender import checksum

class Receiver(object):

    def __init__(self, inbound_port=50005, outbound_port=50006, timeout=10, debug_level=logging.INFO):
        self.logger = utils.Logger(self.__class__.__name__, debug_level)

        self.inbound_port = inbound_port
        self.outbound_port = outbound_port
        self.simulator = channelsimulator.ChannelSimulator(inbound_port=inbound_port, outbound_port=outbound_port,
                                                           debug_level=1)
        self.simulator.rcvr_setup(timeout)
        self.simulator.sndr_setup(timeout)

    def receive(self):
        raise NotImplementedError("The base API class has no implementation. Please override and add your own.")

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

class BogoReceiver(Receiver):
    ACK_DATA = bytes(123)

    def __init__(self):
        super(BogoReceiver, self).__init__()

    def receive(self):
        self.logger.info("Receiving on port: {} and replying with ACK on port: {}".format(self.inbound_port, self.outbound_port))
	previous_packet_num = -1
	next_packet_num = 0
        while True:
            try:
        	data = self.simulator.u_receive()  # receive data
		self.logger.info("Received a packet")
		if data[1] == previous_packet_num:
			self.logger.info("Received duplicate packet num: {}".format(data[1]))
			continue

		previous_packet_num = previous_packet_num + 1
		next_packet_num = next_packet_num + 1
		if next_packet_num > 255:
			next_packet_num = 0
		if previous_packet_num > 255:
			previous_packet_num = 0


		message = data[2:len(data)-1]
		self.logger.info("packet checksum: {}".format(checksum(data[2:1023])))
		if data[0] != checksum(message):
			self.logger.info("Received corrupted packet num: {}".format(data[1]))
			continue

        	self.logger.info("Got data from socket: {}".format(
        		message.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
		sys.stdout.write(message)
		BogoReceiver.ACK_DATA = bytes(data[1]) #sending the packet number back
		self.simulator.u_send(BogoReceiver.ACK_DATA)  # send ACK
		self.logger.info("acking\n")
            except socket.timeout:
                sys.exit()

if __name__ == "__main__":
    # test out BogoReceiver
    rcvr = BogoReceiver()
    rcvr.receive()
