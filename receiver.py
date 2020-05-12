# Written by S. Mevawala, modified by D. Gitzel

import logging

import channelsimulator
import utils
import sys
import socket

class Receiver(object):

	def __init__(self, inbound_port=50005, outbound_port=50006, timeout=10, debug_level=logging.INFO):
		self.logger = utils.Logger(self.__class__.__name__, debug_level)

		self.inbound_port = inbound_port
		self.outbound_port = outbound_port
		self.simulator = channelsimulator.ChannelSimulator(inbound_port=inbound_port, outbound_port=outbound_port,
														   debug_level=debug_level)
		self.simulator.rcvr_setup(timeout)
		self.simulator.sndr_setup(timeout)

	def receive(self):
		raise NotImplementedError("The base API class has no implementation. Please override and add your own.")


class BogoReceiver(Receiver):
	ACK_DATA = bytes(123)

	def __init__(self):
		super(BogoReceiver, self).__init__()

	def receive(self):
		self.logger.info("Receiving on port: {} and replying with ACK on port: {}".format(self.inbound_port, self.outbound_port))
		while True:
			try:
				 data = self.simulator.u_receive()  # receive data
				 self.logger.info("Got data from socket: {}".format(
					 data.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
			 sys.stdout.write(data)
				 self.simulator.u_send(BogoReceiver.ACK_DATA)  # send ACK
			except socket.timeout:
				sys.exit()

class ReliableReceiver(Receiver):
	ACK_DATA = bytes(123)#What should our ack be?
	packet_counter = 0#This will get overwritten by starting_packet_num
	def __init__(self, starting_packet_num = 0):
		'''
		:param starting_packet_num: starting packet number for packet numbers
		'''
		super(ReliableReceiver, self).__init__()
		
		ReliableReceiver.packet_counter = starting_packet_num

	def receive(self):
		self.logger.info("Receiving on port: {} and replying with ACK on port: {}".format(self.inbound_port, self.outbound_port))

		try:
			rcvd_flag = 0
			for i in range(3):
				#Receives datagram
				datagram = self.simulator.u_recieve()#This bytearray includes [checksum,pack_num,data]
				
				#Slices datagram into important sections
				rcvr_checksum = datagram[0]
				packet_num = datagram[1]
				data = datagram[2:]
				
				if (packet_num == packet_counter) and Checksum(data, rcvr_checksum) and (rcvd_flag == 0):
					#We throw out any out of order packets as if they're wrong
					#The checksum checks if packets are wrong. Those are thrown as well
					#The sent_flag insures we don't double coutn any packets
					self.logger.info("Got data from socket: {}".format(data.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
					sys.stdout.write(data)
					self.simulator.u_send(ReliableReceiver.ACK_DATA)  # send ACK
					rcvd_flag = 1
					ReliableReceiver.packet_counter += 1
					ReliableReceiver.packet_counter = ReliableReceiver.packet_counter % 256#Ensures that packet_counter loops
		except socket.timeout:
			pass
		
def Checksum(data, rcvr_checksum):
	'''
	computes checksum of array and compares it to received checksum
	:param data: data to compute checksum on
	:param rcvr_checksum: receieved checksum
	:return result: boolean 1 for success, 0 for failure
	'''
	computed_checksum = 0
	# Checksum computed by adding byte after byte and modulo 255 to keep it in one byte
	for i in data:
		computed_checksum = computed_checksum + i
		computed_checksum = computed_checksum % 255
	result = (computed_checksum == rcvr_checksum)
	return result
		
	

if __name__ == "__main__":
	# test out BogoReceiver
	rcvr = ReliableReceiver()
	rcvr.receive()
