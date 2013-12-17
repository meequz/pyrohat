#! /usr/bin/env python3
# coding: utf-8
import pyaudio, struct, math, wave, random

soundfiles = ['laugh1.wav', 'laugh2.wav', 'laugh4.wav']
CHUNK = 768
TIMES = 80		#~ if chunk = 768, 57 times is one second
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
SHORT_NORMALIZE = 1.0 / 32768.0
TRESH = 9 / 100
WAIT_AFTER_LAUGH = 40	#~ not seconds

def get_rms(block):
	count = len(block)/2
	format = "%dh"%(count)
	shorts = struct.unpack(format, block)
	sum_squares = 0.0	# iterate over the block
	for sample in shorts:
		n = sample * SHORT_NORMALIZE
		sum_squares += n*n
	return math.sqrt(sum_squares / count)
def add_to_stack(stack, maxlen, what_add):
	stack.append(what_add)
	if len(stack) > maxlen: del stack[0]
def play():
	wf = wave.open(random.choice(soundfiles), 'rb')
	p = pyaudio.PyAudio()
	stream = p.open(format=p.get_format_from_width(wf.getsampwidth()), channels=wf.getnchannels(), rate=wf.getframerate(), output=True)
	data = wf.readframes(CHUNK)
	while data != '':
		stream.write(data)
		data = wf.readframes(CHUNK)
	stream.stop_stream()
	stream.close()
	p.terminate()

while True:
	p = pyaudio.PyAudio()
	stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

	last_levels = []
	canplay = False
	while True:
		level = get_rms(stream.read(CHUNK))
		add_to_stack(stack=last_levels, maxlen=TIMES, what_add=level)
		average = sum(last_levels) / len(last_levels)

		if average < TRESH  and  canplay:
			canplay = False
			play()
			break
		if average > TRESH:  canplay = True

	stream.stop_stream()
	stream.close()
	p.terminate()
