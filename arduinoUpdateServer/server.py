from bottle import Bottle, run, get, abort, static_file, request, response
import json as json
import os
import sys
from datetime import datetime
from functools import wraps
import logging
from paste import httpserver


# Create basepath
path = os.path.dirname(os.path.realpath(__file__))

# Log events to stdout
logger = logging.getLogger()
logger.setLevel(logging.INFO)

stdoutHandler = logging.StreamHandler(sys.stdout)
stdoutHandler.setLevel(logging.INFO)

formatter = logging.Formatter('%(msg)s')
stdoutHandler.setFormatter(formatter)

logger.addHandler(stdoutHandler)

# Read options file
logging.info("Reading options file: /data/options.json")

with open(path + '/data/options.json', mode='r') as data_file:
    options = json.load(data_file)


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

def needsUpdateVersion(deviceVersion, latestVersion):
	deviceVersion = deviceVersion.split('.')
	latestVersion = latestVersion.split('.')

	if (latestVersion[0] > deviceVersion[0]):
		return True
	
	if (latestVersion[1] > deviceVersion[1]):
		return True

	if (latestVersion[2] > deviceVersion[2]):
		return True

	return False


def getFirmwareLatestVersion(firmware_name):
	for firmware in options["firmwares"]:
		if (firmware["name"] == firmware_name):
			return firmware["version"]
		else:
			return ""

def getFirmwareRelativePath(firmware):
	return "/share/arduinoUpdateServer/" + firmware + "/"

def getFirmwareData(firmware, device):
	firmwareData = {}
	firmware_version = getFirmwareLatestVersion(firmware)
	firmware_path = getFirmwareRelativePath(firmware) + firmware_version + "/" + device + "/firmware.bin"
	spiffs_path = getFirmwareRelativePath(firmware) + firmware_version + "/" + device + "/spiffs.bin"

	if not (os.path.exists(os.path.realpath(os.getcwd() + firmware_path))):
		firmware_path = ""

	if not (os.path.exists(os.path.realpath(os.getcwd() + spiffs_path))):
		spiffs_path = ""

	if firmware_path:
		firmwareData["version"] = firmware_version
		firmwareData["firmware"] = firmware + "/" + firmware_version + "/" + device + "/firmware.bin"
		firmwareData["spiffs"] = firmware + "/" + firmware_version + "/" + device + "/spiffs.bin"

	return firmwareData


###############################################################################

server = Bottle()

server.install(log_to_logger)


@server.get('/status')
def getStatus():
	return {'OK'}

@server.get('/firmwares/<fw_name>/<fw_version>/<device>/<file_bin>')
def getFirmwarefirmwareDataBin(fw_name, fw_version, device, file_bin):
	return static_file(file_bin, root=os.path.realpath(os.getcwd() + getFirmwareRelativePath(fw_name) + fw_version + "/" + device + "/"), download=file_bin)

@server.get('/<fw_name>/<version>/<device>')
def getUpdate(fw_name, version, device):
	for firmware in options["firmwares"]:
		if (fw_name == firmware['name']):
			if (needsUpdateVersion(version, getFirmwareLatestVersion(firmware['name']))):
				if (device in firmware['devices']):
					return json.dumps(getFirmwareData(fw_name, device))
				else:
					abort(404, "Device not found.")
			else:
				return {'{}'}
		else:
			abort(404, "Firmware not found.")

httpserver.serve(server, host='0.0.0.0', port=8266)
