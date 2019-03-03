#!/usr/bin/python
from ky040.KY040 import KY040
import time
import RPi.GPIO as GPIO
import subprocess
from volumio import Volumio

class BitFilter():

	def __init__(self):

		self.bits = []
		self.last_update = 0.0

	def update(self, value):
		self.bits.append(value)
		self.bits = self.bits[-2:] 
		print(self.bits)

		result = None
		delta = time.time() - self.last_update
		print(delta)
		if len(self.bits)<2 or delta > 0.5: 
			result = True
		else:
			result = self.bits[0] == self.bits[1]

		self.last_update = time.time()
		
		return result


class Controller():

	def __init__(self,STEP_VOL):
		self.v = Volumio()
		self.volume = 0
		self.STEP_VOL = STEP_VOL

		self.filter=BitFilter()

		while len(self.v._state)==0:
			time.sleep(0.1)

		self.volume=self.v.volume()
		print('* Initial volume set to', self.volume)


	def rotaryChange(self, direction):
		print "turned - " + str(direction)
		if self.filter.update(direction):
			if direction == 0:
				self.volume_change(self.STEP_VOL)
			else:
				self.volume_change(-self.STEP_VOL)

	def volume_change(self, step):
		self.volume = self.volume + step
		if self.volume > 100: self.volume = 100
		elif self.volume <0 : self.volume = 0
		self.v.set_volume(self.volume)
		print('* vol:', self.volume)

	def switchPressed(self):
		 self.v._send('toggle')
		 print('* Toggle')

if __name__=='__main__':

	# Configs
	CLOCKPIN = 24
	DATAPIN = 23
	SWITCHPIN = 22
	STEP_VOL = 15

	c = Controller(STEP_VOL)

	ky040 = KY040(CLOCKPIN, DATAPIN, SWITCHPIN, c.rotaryChange, c.switchPressed)
	ky040.start()
		
	# Keep your proccess running
	try:
			while True:
				time.sleep(0.1)
	finally:
			ky040.stop()
			GPIO.cleanup()
