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

formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
stdoutHandler.setFormatter(formatter)

logger.addHandler(stdoutHandler)

# Warning Firmware Storage
logging.warning("Ensure firmware files (firmware.bin & spiffs.bin) are placed following this directory structure: \"/share/arwiupser/<firmware_name>/<firmware_latest_version>/<device>\"")
logging.warning("Remember spiffs.bin is not always necessary")
logging.warning("Optional: You can set an invalid firmware, version or device with INVALID ending like so: <firmware_name>INVALID/<firmware_latest_version>INVALID/<device>INVALID")


def log_to_logger(fn):
    '''
    Wrap a Bottle request so that a log line is emitted after it's handled.
    (This decorator can be extended to take the desired logger as a param.)
    '''
    @wraps(fn)
    def _log_to_logger(*args, **kwargs):
        actual_response = fn(*args, **kwargs)
        logger.info('%s %s %s %s' % (request.remote_addr,
                                     request.method,
                                     request.url,
                                     response.status))
        return actual_response
    return _log_to_logger

def getFirmwareRelativePath(firmware_name):
	return "/share/arwiupser/"

def getFirmwareNameRelativePath(firmware_name):
	return getFirmwareRelativePath(firmware_name) + firmware_name + "/"

def getFimrwareRealPath(firmware_name):
	return os.path.realpath(os.getcwd() + getFirmwareRelativePath(firmware_name))

def getFimrwareNameRealPath(firmware_name):
	return os.path.realpath(os.getcwd() + getFirmwareNameRelativePath(firmware_name))

def getFimrwareVersionRealPath(firmware_name, firmware_version):
	return os.path.realpath(os.getcwd() + getFirmwareNameRelativePath(firmware_name) + firmware_version + "/")

def getFimrwareDeviceRealPath(firmware_name, firmware_version, device):
	return os.path.realpath(os.getcwd() + getFirmwareNameRelativePath(firmware_name) + firmware_version + "/" + device + "/")

def checkFirmwareList(firmware_name):
	return (firmware_name in os.listdir(getFimrwareRealPath(firmware_name)))

def checkFirmware(firmware_name, firmware_version, device):
	return os.path.exists(getFimrwareDeviceRealPath(firmware_name, firmware_version, device))

def getFirmwareLatestVersion(firmware_name, device):
	versions = os.listdir(getFimrwareNameRealPath(firmware_name))

	versions.sort(reverse=True)

	for version in versions:
		if (checkFirmware(firmware_name, version, device) and not version.endswith("INVALID")):
			return version

	return ""

def checkFirmwareFileExists(firmware_name, firmware_version, device):
	return os.path.exists(getFimrwareDeviceRealPath(firmware_name, firmware_version, device) + "/firmware.bin")

def checkSpiffsFileExists(firmware_name, firmware_version, device):
	return os.path.exists(getFimrwareDeviceRealPath(firmware_name, firmware_version, device) + "/spiffs.bin")

def getFirmwareData(firmware_name, firmware_version, device):
	firmwareData = {}

	if checkFirmwareFileExists(firmware_name, firmware_version, device):
		firmwareData["version"] = firmware_version
		firmwareData["firmware"] = firmware_name + "/" + firmware_version + "/" + device + "/firmware.bin"

	if checkSpiffsFileExists(firmware_name, firmware_version, device):
		firmwareData["spiffs"] = firmware_name + "/" + firmware_version + "/" + device + "/spiffs.bin"

	return firmwareData


###############################################################################

server = Bottle()

server.install(log_to_logger)


@server.get('/status')
def getStatus():
	return {'OK'}

@server.get('/<firmware_name>/<firmware_version>/<device>')
def getUpdate(firmware_name, firmware_version, device):
	if (checkFirmwareList(firmware_name)):

		latest_version = getFirmwareLatestVersion(firmware_name, device)

		if not latest_version:
			abort(404, "Firmware latest version not found.")

		elif (firmware_version < latest_version):

			if (checkFirmwareFileExists(firmware_name, latest_version, device)):
				return json.dumps(getFirmwareData(firmware_name, latest_version, device))
			else:
				abort(404, "Firmware files not found.")
		else:
			return {'{}'}
	else:
		abort(404, "Firmware not found.")

@server.get('/<firmware_name>/<firmware_version>/<device>/<file_bin>')
def getFirmwarefirmwareDataBin(firmware_name, firmware_version, device, file_bin):
	return static_file(file_bin, root=getFimrwareDeviceRealPath(firmware_name, firmware_version, device), download=file_bin)

httpserver.serve(server, host='0.0.0.0', port=8266)
