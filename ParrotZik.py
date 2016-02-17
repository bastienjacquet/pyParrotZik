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
'''
API string from https://github.com/devmil/parrot-zik-2-supercharge
     ACCOUNT_USERNAME_GET = "/api/account/username/get"
     ACCOUNT_USERNAME_SET = "/api/account/username/set"
     APPLI_VERSION_SET = "/api/appli_version/set"
     AUDIO_NOISE_GET = "/api/audio/noise/get"
     AUDIO_PARAM_EQ_VALUE_SET = "/api/audio/param_equalizer/value/set"
     AUDIO_PRESET_ACTIVATE = "/api/audio/preset/activate"
     AUDIO_PRESET_BYPASS_GET = "/api/audio/preset/bypass/get"
     AUDIO_PRESET_BYPASS_SET = "/api/audio/preset/bypass/set"
     AUDIO_PRESET_CLEAR_ALL = "/api/audio/preset/clear_all"
     AUDIO_PRESET_COUNTER_GET = "/api/audio/preset/counter/get"
     AUDIO_PRESET_CURRENT_GET = "/api/audio/preset/current/get"
     AUDIO_PRESET_DOWNLOAD = "/api/audio/preset/download"
     AUDIO_PRESET_PRODUCER_CANCEL = "/api/audio/preset/cancel_producer"
     AUDIO_PRESET_REMOVE = "/api/audio/preset/remove"
     AUDIO_PRESET_SAVE = "/api/audio/preset/save"
     AUDIO_PRESET_SYNCHRO_START = "/api/audio/preset/synchro/start"
     AUDIO_PRESET_SYNCHRO_STOP = "/api/audio/preset/synchro/stop"
     AUDIO_SMART_TUNE_GET = "/api/audio/smart_audio_tune/get"
     AUDIO_SMART_TUNE_SET = "/api/audio/smart_audio_tune/set"
     AUDIO_SOURCE_GET = "/api/audio/source/get"
     AUDIO_TRACK_METADATA_GET = "/api/audio/track/metadata/get"
     BATTERY_GET = "/api/system/battery/get"
     CONCERT_HALL_ANGLE_GET = "/api/audio/sound_effect/angle/get"
     CONCERT_HALL_ANGLE_SET = "/api/audio/sound_effect/angle/set"
     CONCERT_HALL_ENABLED_GET = "/api/audio/sound_effect/enabled/get"
     CONCERT_HALL_ENABLED_SET = "/api/audio/sound_effect/enabled/set"
     CONCERT_HALL_GET = "/api/audio/sound_effect/get"
     CONCERT_HALL_ROOM_GET = "/api/audio/sound_effect/room_size/get"
     CONCERT_HALL_ROOM_SET = "/api/audio/sound_effect/room_size/set"
     EQUALIZER_ENABLED_GET = "/api/audio/equalizer/enabled/get"
     EQUALIZER_ENABLED_SET = "/api/audio/equalizer/enabled/set"
     FRIENDLY_NAME_GET = "/api/bluetooth/friendlyname/get"
     FRIENDLY_NAME_SET = "/api/bluetooth/friendlyname/set"
     NOISE_CONTROL_ENABLED_GET = "/api/audio/noise_control/enabled/get"
     NOISE_CONTROL_ENABLED_SET = "/api/audio/noise_control/enabled/set"
     NOISE_CONTROL_GET = "/api/audio/noise_control/get"
     NOISE_CONTROL_SET = "/api/audio/noise_control/set"
     SOFTWARE_DOWNLOAD_SIZE_SET = "/api/software/download_size/set"
     SOFTWARE_TTS_DISABLE = "/api/software/tts/disable"
     SOFTWARE_TTS_ENABLE = "/api/software/tts/enable"
     SOFTWARE_TTS_GET = "/api/software/tts/get"
     SOFTWARE_VERSION_SIP6_GET = "/api/software/version/get"
     SYSTEM_ANC_PHONE_MODE_GET = "/api/system/anc_phone_mode/enabled/get"
     SYSTEM_ANC_PHONE_MODE_SET = "/api/system/anc_phone_mode/enabled/set"
     SYSTEM_AUTO_CONNECTION_GET = "/api/system/auto_connection/enabled/get"
     SYSTEM_AUTO_CONNECTION_SET = "/api/system/auto_connection/enabled/set"
     SYSTEM_AUTO_POWER_OFF_GET = "/api/system/auto_power_off/get"
     SYSTEM_AUTO_POWER_OFF_LIST_GET = "/api/system/auto_power_off/presets_list/get"
     SYSTEM_AUTO_POWER_OFF_SET = "/api/system/auto_power_off/set"
     SYSTEM_BT_ADDRESS_GET = "/api/system/bt_address/get"
     SYSTEM_COLOR_GET = "/api/system/color/get"
     SYSTEM_DEVICE_PI = "/api/system/pi/get"
     SYSTEM_FLIGHT_MODE_DISABLE = "/api/flight_mode/disable"
     SYSTEM_FLIGHT_MODE_ENABLE = "/api/flight_mode/enable"
     SYSTEM_FLIGHT_MODE_GET = "/api/flight_mode/get"
     SYSTEM_HEAD_DETECTION_ENABLED_GET = "/api/system/head_detection/enabled/get"
     SYSTEM_HEAD_DETECTION_ENABLED_SET = "/api/system/head_detection/enabled/set"
     SYSTEM__DEVICE_TYPE_GET = "/api/system/device_type/get"
     THUMB_EQUALIZER_VALUE_GET = "/api/audio/thumb_equalizer/value/get"
     THUMB_EQUALIZER_VALUE_SET = "/api/audio/thumb_equalizer/value/set"
'''

