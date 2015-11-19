import wave
import sys
import struct
import os
import time
from random import randint


def load_file(fin):
	"""
	Load data from target .wav file
	:param fin: Path to target .wav file
	:return info: Parameters of .wav file
	:return frame_list: List of frames for .wav file
	"""
	ip = wave.open(fin, 'r')
	info = ip.getparams()
	frame_list = []
	for i in range(ip.getnframes()):
		sframe = ip.readframes(1)
		amplitude = struct.unpack('<h', sframe)[0]
		frame_list.append(amplitude)
	ip.close()

	for i in range(0,len(frame_list)):
		if abs(frame_list[i]) < 25:
			frame_list[i] = 0

	return info, frame_list


def get_chunks(info, frame_list):
	"""
	Detect loud parts of the sound file and seperate them into chunks
	:param info: Parameters of .wav file
	:param frame_list: List of frames for .wav file
	:return chunks: List of sound chunks
	"""
	thresh = 30
	output = []
	nonzerotemp = []
	length = len(frame_list)
	i = 0

	while i < length:
	    zeros = []
	    while i < length and frame_list[i] == 0:
	        i += 1
	        zeros.append(0)
	    if len(zeros) != 0 and len(zeros) < thresh:
	        nonzerotemp += zeros
	    elif len(zeros) > thresh:
	        if len(nonzerotemp) > 0 and i < length:
	            output.append(nonzerotemp)
	            nonzerotemp = []
	    else:
	        nonzerotemp.append(frame_list[i])
	        i += 1
	if len(nonzerotemp) > 0:
	    output.append(nonzerotemp)

	chunks = []
	for j in range(0,len(output)):
		if len(output[j]) > 3000:
			chunks.append(output[j])


	return chunks

def modify_chunks(chunks, inc_percent = 1):
	"""
	Modify size of chunks by a set amount (default: 10%)
	:param chunks: List of sound chunks
	:param inc_percent: Amount to enlarge chunks
	:return chunks: List of modified sound chunks
	"""

	for l in chunks:
		for m in range(0,len(l)):
			if l[m] == 0:
				 l[m] = randint(-0,+0)

	for l in chunks:
		for m in range(0,len(l)):
			if l[m] <= 0:
				# negative value
				l[m] = 0 - abs(l[m]) + abs(l[m])*inc_percent/100
			else:
				#positive vaule
				l[m] =     abs(l[m]) + abs(l[m])*inc_percent/100

	return chunks

def split_wav(info, chunks, out):
	"""
	Stores all chunks in seperate .wav files
	:param info: Parameters for .wav files
	:param chunks: List of sound chunks
	:param out: Directory to store output .wav files
	"""

	NEW_RATE = 1

	for i in range(0, len(chunks)):
		new_frame_rate = info[0]*NEW_RATE
		split = wave.open(out + str(i)+'.wav', 'w')
		split.setparams((info[0],info[1],info[2],0,info[4],info[5]))

		#Add some silence at start selecting
		for k in range(0,10000):
			single_frame = struct.pack('<h', randint(-25,+25))
			split.writeframes(single_frame)

		# Add the voice for the first time
		for frames in chunks[i]:
			single_frame = struct.pack('<h', frames)
			split.writeframes(single_frame)

		#Add some silence in between two digits
		for k in range(0,10000):
			single_frame = struct.pack('<h', randint(-25,+25))
			split.writeframes(single_frame)

		#Add silence at end
		for k in range(0,10000):
			single_frame = struct.pack('<h', randint(-25,+25))
			split.writeframes(single_frame)

		split.close()