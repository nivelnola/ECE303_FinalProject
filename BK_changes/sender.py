# Written by S. Mevawala, modified by D. Gitzel

import logging
import socket
import numpy
import channelsimulator
import utils
import sys

class Sender(object):

    def __init__(self, inbound_port=50006, outbound_port=50005, timeout=3, debug_level=logging.INFO):
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


def make_frame(data, num):
	array = bytearray(1025)
	array[0] = checksum(data)
	array[1] = num

	array[2:1024] = data
	print array[2:1024].decode('ascii')
	return array


class ReliableSender(Sender):
	def __init__(self):
		super(ReliableSender, self).__init__()

	def send(self, data):
		self.logger.info("Sending on port: {} and waiting for ACK on port: {}".format(self.outbound_port, self.inbound_port))
		#print "Sending on port: {} and waiting for ACK on port: {}".format(self.outbound_port, self.inbound_port)
		#frame = make_frame(data)

		length = len(data)
		#print length
		ticker = 0
		string = ''
		'''
		for i in range(0,1022):
			if ticker <length:
				string = string + str(data[ticker])
				ticker = ticker + 1
			frame = make_frame(string)
			self.send_frame(frame)
		'''
		previous_packet_num = -1
		next_packet_num = 0
		for frameTicker in range(0,(length / 1022)+1):
			#print "numpy.ceil: " + str(int(numpy.ceil(length / 1022))+1)
			currData = data[(1022*frameTicker):min(1022*(frameTicker+1)-1, length)]
			frame = make_frame(currData, next_packet_num)
			print "frame[0]  = " + str(frame[0])
			print "frame[1] = "  + str(frame[1])
			print "ticker low = " + str(1022*frameTicker) 
			print " | high = " + str(min(1022*(frameTicker+1)-1, length))
			self.send_frame(frame, next_packet_num)
			print "received ack for sure"
			previous_packet_num = previous_packet_num + 1
			next_packet_num = next_packet_num + 1
			if next_packet_num > 255:
				next_packet_num = 0
			if previous_packet_num > 255:
				previous_packet_num = 0			


		'''

		prev_cutoff = 0
		for i in range(0, length):
			if i >= 1022 + prev_cutoff
				prev_cutoff = i
				continue
			string = string + data[i]
			frame = make_frame(string)
			self.send_frame(frame)
		'''

	def send_frame(self, frame, num):
		while True:
			try:
				self.simulator.u_send(frame)  # send data

				print "Sent frame, cheksum num = {}, number = {}\n".format(frame[0], frame[1])
				#self.logger.info("Send data: {} 3 times".format(frame[2:1023]))
		        	ack = self.simulator.u_receive()  # receive ACK
				print type(ack)
				#if ack[0] > 255:
				#	self.logger.info("Got corrupt ACK from socket: {}, num: {}".format(ack, num))  
				#	continue

				try:
					if ack.decode('ascii') != str(num):
						self.logger.info("Got wrong ACK from socket: {}, num: {}".format(ack[0], num))  
						continue
				except:
					self.logger.info("Got corrupt ACK from socket: {}, num: {}".format(ack, num))  
					continue
        			#self.logger.info("Got right ACK from socket: {}".format(
					#ack.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
				print "about to break"
				self.logger.info("Good Ack, NUM: {}".format(ack))
				break
			except socket.timeout:
				pass




if __name__ == "__main__":
    # test out BogoSender
    DATA = bytearray(sys.stdin.read())
    sndr = ReliableSender()
    sndr.send(DATA)
