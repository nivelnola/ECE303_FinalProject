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
														   debug_level=debug_level)
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

############
class ReliableSender(Sender):

	def __init__(self, starting_packet_num = 0, timeout = 1):
		'''
		:param starting_packet_num: starting packet number for packet numbers
		:param timeout: timeout of sender to trigger resend, may use later
		'''
		super(ReliableSender, self).__init__()
		
		self.timeout = timeout
		self.packet_num = starting_packet_num
		self.simulator.sndr_socket.settimeout(timeout)

	def send(self, data):
		#Create DataGram object
		datagram = DataGram(data, self.packet_num) 

		# Turn it into a bytearray for sending through the channel
		byte_datagram = bytearray([checksum, packet_num, data]) 

		# Send the data and wait for a good ACK
		while True: 
			try:
				# Send 3 times
				for i in range(0,3): 
					self.simulator.u_send(byte_datagram)
	
				# Wait for ACK
				ack = self.simulator.u_recieve()

				if ack == packet_num: # correct ACK ->  break
					break

				else:
					send(data) # wrong ACK -> resend
				break
			except socket.timeout:
				pass

class DataGram(object):
	def __init__(self, data, packetNum):
		'''
		:param data: data inside the packet
		:param packetNUM: number of the packet being sent
		'''
		self.data = data
		self.packet_num = packetNum
		self.checksum = Checksum(data)

	def Checksum(self, data):
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
	
if __name__ == "__main__":
	# test out BogoSender
	DATA = bytearray(sys.stdin.read())
	sndr = ReliableSender()
	sndr.send(DATA)
