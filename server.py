from bottle import run, get, static_file
import json as json
import os
import sys

##################### sonoff-danimtb FW and binary files ######################

sonoffdanimtb_last_version = "0.0.6"
sonoffdanimtb_sonoff_bin = "/firmwares/sonoff-danimtb_v0.0.6_sonoff.bin"
sonoffdanimtb_sonoffs20_bin = "/firmwares/sonoff-danimtb_v0.0.6_sonoffs20.bin"
sonoffdanimtb_sonofftouch_bin = "/firmwares/sonoff-danimtb_v0.0.6_sonofftouch.bin"
sonoffdanimtb_sonofftouchesp01_bin = "/firmwares/sonoff-danimtb_v0.0.6_sonofftouchesp01.bin"

sonoff_data = {}
sonoff_data["version"] = sonoffdanimtb_last_version
sonoff_data["fw"] = sonoffdanimtb_sonoff_bin
sonoff_data["spiffs"] = ""

sonoffs20_data = {}
sonoffs20_data["version"] = sonoffdanimtb_last_version
sonoffs20_data["fw"] = sonoffdanimtb_sonoffs20_bin

sonofftouch_data = {}
sonofftouch_data["version"] = sonoffdanimtb_last_version
sonofftouch_data["fw"] = sonoffdanimtb_sonofftouch_bin

sonofftouchesp01_data = {}
sonofftouchesp01_data["version"] = sonoffdanimtb_last_version
sonofftouchesp01_data["fw"] = sonoffdanimtb_sonofftouchesp01_bin


###############################################################################

@get('/status')
def getStatus():
	return {'OK'}

@get('/firmwares/<fw_bin>')
def getFirmwareSonoffDanimtbBin(fw_bin):
	firmware_path = 'firmwares' + fw_bin
	return static_file(fw_bin, root=os.getcwd()+'/firmwares/', download=fw_bin)

@get('/<fw>/<version>/<type>')
def getUpdate(fw, version, type):
	if (fw == 'sonoff-danimtb'):
		if(version < sonoffdanimtb_last_version):
			if(type == 'sonoff'):
				return json.dumps(sonoff_data)
			elif(type == 'sonoff-s20'):
				return json.dumps(sonoffs20_data)
			elif(type == 'sonoff-touch'):
				return json.dumps(sonofftouch_data)
			elif(type == 'sonoff-touch-esp01'):
				return json.dumps(sonofftouchesp01_data)
			else:
				return {'Device not supported'}
		else:
			return {'{}'}
	else:
		return {'{}'}


run(host='0.0.0.0', port=sys.argv[1])
