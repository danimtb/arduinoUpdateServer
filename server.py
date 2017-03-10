from bottle import run, get, abort, static_file
import json as json
import os
import sys


##################### sonoff-danimtb FW and binary files ######################

sonoffdanimtb_last_version = "0.0.9"
sonoffdanimtb_path = "/firmwares/sonoff-danimtb/"

def sonoffdanimtb_pathGenerator(device):
	sonoffdanimtb = {}
	version = sonoffdanimtb_last_version
	firmware_path = sonoffdanimtb_path + sonoffdanimtb_last_version + "/" + device + "/firmware.bin"
	spiffs_path = sonoffdanimtb_path + sonoffdanimtb_last_version + "/" + device + "/spiffs.bin"

	if not (os.path.exists(os.path.realpath(os.getcwd() + firmware_path))):
		print os.path.realpath(os.getcwd() + firmware_path)
		firmware_path = ""

	if not (os.path.exists(os.path.realpath(os.getcwd() + spiffs_path))):
		spiffs_path = ""

	if firmware_path and spiffs_path:
		sonoffdanimtb["version"] = version
		sonoffdanimtb["fw"] = firmware_path
		sonoffdanimtb["spiffs"] = spiffs_path

	return sonoffdanimtb

###############################################################################


@get('/status')
def getStatus():
	return {'OK'}

@get('/firmwares/<fw_name>/<fw_version>/<device>/<file_bin>')
def getFirmwareSonoffDanimtbBin(fw_name, fw_version, device, file_bin):
	return static_file(file_bin, root=os.path.realpath(os.getcwd() + '/firmwares/' + fw_name + "/" + fw_version + "/" + device + "/"), download=file_bin)

@get('/<fw>/<version>/<device>')
def getUpdate(fw, version, device):
	if (fw == 'sonoff-danimtb'):
		if(version < sonoffdanimtb_last_version):
			if(device == 'sonoff'):
				return json.dumps(sonoffdanimtb_pathGenerator(device))
			elif(device == 'sonoff-s20'):
				return json.dumps(sonoffdanimtb_pathGenerator(device))
			elif(device == 'sonoff-touch'):
				return json.dumps(sonoffdanimtb_pathGenerator(device))
			elif(device == 'sonoff-touch-esp01'):
				return json.dumps(sonoffdanimtb_pathGenerator(device))
			else:
				abort(404, "Device not found.")
		else:
			return {'{}'}
	else:
		abort(404, "Firmware not found.")


run(host='0.0.0.0', port=sys.argv[1])