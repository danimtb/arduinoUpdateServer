from bottle import Bottle, run, get, abort, static_file, request, response
import json as json
import os
import sys
from datetime import datetime
from functools import wraps
import logging
from paste import httpserver


#### LOGGER

logger = logging.getLogger('access')

# set up the logger
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('access.log')
formatter = logging.Formatter('%(msg)s')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def log_to_logger(fn):
    '''
    Wrap a Bottle request so that a log line is emitted after it's handled.
    (This decorator can be extended to take the desired logger as a param.)
    '''
    @wraps(fn)
    def _log_to_logger(*args, **kwargs):
        request_time = datetime.now()
        actual_response = fn(*args, **kwargs)
        # modify this to log exactly what you need:
        logger.info('%s %s %s %s %s' % (request.remote_addr,
                                        request_time,
                                        request.method,
                                        request.url,
                                        response.status))
        return actual_response
    return _log_to_logger


########


########## HELPERS

def getFirmwareVersion(firmware):
	firmwaresJson = open("firmwares.json")
	firmwares = json.load(firmwaresJson)
	return firmwares[firmware]["version"]


def getFirmwareRelativePath(firmware):
	firmwaresJson = open("firmwares.json")
	firmwares = json.load(firmwaresJson)
	return firmwares[firmware]["path"]


def getFirmwareData(firmware, device):
	firmwareData = {}
	firmware_version = getFirmwareVersion(firmware)
	firmware_path = getFirmwareRelativePath(firmware) + firmware_version + "/" + device + "/firmware.bin"
	spiffs_path = getFirmwareRelativePath(firmware) + firmware_version + "/" + device + "/spiffs.bin"

	if not (os.path.exists(os.path.realpath(os.getcwd() + firmware_path))):
		firmware_path = ""

	if not (os.path.exists(os.path.realpath(os.getcwd() + spiffs_path))):
		spiffs_path = ""

	if firmware_path and spiffs_path:
		firmwareData["version"] = firmware_version
		firmwareData["firmware"] = firmware_path
		firmwareData["spiffs"] = spiffs_path

	return firmwareData

###############################################################################

server = Bottle()

server.install(log_to_logger)


@server.get('/status')
def getStatus():
	return {'OK'}

@server.get('/firmwares/<fw_name>/<fw_version>/<device>/<file_bin>')
def getFirmwarefirmwareDataBin(fw_name, fw_version, device, file_bin):
	return static_file(file_bin, root=os.path.realpath(os.getcwd() + '/firmwares/' + fw_name + "/" + fw_version + "/" + device + "/"), download=file_bin)

@server.get('/<fw>/<version>/<device>')
def getUpdate(fw, version, device):
	if (fw == 'sonoff-danimtb'):
		if(version < getFirmwareVersion('sonoff-danimtb')):
			if(device == 'sonoff'):
				return json.dumps(getFirmwareData(fw, device))
			elif(device == 'sonoff-s20'):
				return json.dumps(getFirmwareData(fw, device))
			elif(device == 'sonoff-touch'):
				return json.dumps(getFirmwareData(fw, device))
			elif(device == 'sonoff-touch-esp01'):
				return json.dumps(getFirmwareData(fw, device))
			elif(device == 'sonoff-pow'):
				return json.dumps(getFirmwareData(fw, device))
			else:
				abort(404, "Device not found.")
		else:
			return {'{}'}
	else:
		abort(404, "Firmware not found.")

httpserver.serve(server, host='0.0.0.0', port=sys.argv[1])
