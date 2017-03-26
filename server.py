from bottle import Bottle, run, get, abort, static_file, request, response
import json as json
import os
import sys
from datetime import datetime
from functools import wraps
import logging


##################### sonoff-danimtb FW and binary files ######################

sonoffdanimtb_last_version = "0.1.0"
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

server = Bottle()

server.install(log_to_logger)


@server.get('/status')
def getStatus():
	return {'OK'}

@server.get('/firmwares/<fw_name>/<fw_version>/<device>/<file_bin>')
def getFirmwareSonoffDanimtbBin(fw_name, fw_version, device, file_bin):
	return static_file(file_bin, root=os.path.realpath(os.getcwd() + '/firmwares/' + fw_name + "/" + fw_version + "/" + device + "/"), download=file_bin)

@server.get('/<fw>/<version>/<device>')
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


server.run(host='0.0.0.0', port=sys.argv[1])