#!/usr/bin/env python

import sys
if sys.platform == "darwin":
	import lightblue
else:
	import bluetooth

import ParrotProtocol
import struct
from BeautifulSoup import BeautifulSoup

class ParrotZik(object):
	def __init__(self,addr=None):
		uuid = "0ef0f502-f0ee-46c9-986c-54ed027807fb"


		if sys.platform == "darwin":
			service_matches = lightblue.findservices( name = "Parrot RFcomm service", addr = addr )
		else:
			service_matches = bluetooth.find_service( name = "Parrot RFcomm service", address = addr )


		if len(service_matches) == 0:
		    print "Failed to find Parrot Zik RFCOMM service"
		    self.sock =""
		    return

		if sys.platform == "darwin":
			first_match = service_matches[0]
			port = first_match[1]
			name = first_match[2]
			host = first_match[0]
		else:
			first_match = service_matches[0]
			port = first_match["port"]
			name = first_match["name"]
			host = first_match["host"]

		print "Connecting to \"%s\" on %s" % (name, host)

		if sys.platform == "darwin":
			self.sock=lightblue.socket()
		else:
			self.sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )

		self.sock.connect((host, port))

		self.sock.send('\x00\x03\x00')
		data = self.sock.recv(1024)

		self.BatteryLevel = 100
		self.BatteryCharging = False
		self.Version = float(self.getVersion())
		print "Connected"

	def getBatteryState(self):
		data = self.sendGetMessage("/api/system/battery/get")
		return data.answer.system.battery["state"]

	def getBatteryLevel(self):
		data = self.sendGetMessage("/api/system/battery/get")	
		try:
			if data.answer.system.battery.get("level"):
				self.BatteryLevel = data.answer.system.battery["level"]
			if data.answer.system.battery.get("percent"):
				self.BatteryLevel = data.answer.system.battery["percent"]
			if data.answer.system.battery["state"] == 'charging':
				self.BatteryCharging = True
			else:
				self.BatteryCharging = False
		except:
			pass

		try:
			print "notification received" + data.notify["path"]
		except:
			pass

		return self.BatteryLevel

	def getVersion(self):
		data = self.sendGetMessage("/api/software/version/get")
		if data.answer.software.get("version"):
			return data.answer.software["version"]
		elif data.answer.software.get("sip6"):
			return data.answer.software["sip6"]
		else:
			return -1

	def getFriendlyName(self):
		data = self.sendGetMessage("/api/bluetooth/friendlyname/get")
		return data.answer.bluetooth["friendlyname"]

	def getAutoConnection(self):
		data = self.sendGetMessage("/api/system/auto_connection/enabled/get")
		return data.answer.system.auto_connection["enabled"]

	def setAutoConnection(self,arg):
		data = self.sendSetMessage("/api/system/auto_connection/enabled/set",arg)
		return data

	def getAncPhoneMode(self):
		data = self.sendGetMessage("/api/system/anc_phone_mode/enabled/get")
		return data.answer.system.anc_phone_mode["enabled"]

	def getNoiseCancel(self):
		data = self.sendGetMessage("/api/audio/noise_cancellation/enabled/get")
		return data.answer.audio.noise_cancellation["enabled"]

	def setNoiseCancel(self,arg):
		data = self.sendSetMessage("/api/audio/noise_cancellation/enabled/set",arg)
		return data

	def getLouReedMode(self):
		if self.Version > 2.00:
			return 0
		data = self.sendGetMessage("/api/audio/specific_mode/enabled/get")
		return data.answer.audio.specific_mode["enabled"]

	def setLouReedMode(self,arg):
		if self.Version > 2.00:
			return 0
		data = self.sendSetMessage("/api/audio/specific_mode/enabled/set",arg)
		return data

	def getParrotConcertHall(self):
		data = self.sendGetMessage("/api/audio/sound_effect/enabled/get")
		return data.answer.audio.sound_effect["enabled"]

	def setParrotConcertHall(self,arg):
		data = self.sendSetMessage("/api/audio/sound_effect/enabled/set",arg)
		return data

	def sendGetMessage(self,message):
		message = ParrotProtocol.getRequest(message)
		return self.sendMessage(message)

	def sendSetMessage(self,message,arg):
		message = ParrotProtocol.setRequest(message,arg)
		return self.sendMessage(message)

	def sendMessage(self,message):
		try:
			self.sock.send(str(message))
		except:
			self.sock =""
			return
		if sys.platform == "darwin":
			data = self.sock.recv(30)
		else:
			data = self.sock.recv(7)
		data = self.sock.recv(1024)
		data=BeautifulSoup(data)
		return data

	def Close(self):
		self.sock.close()