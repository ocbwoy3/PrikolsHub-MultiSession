# PrikolsHub Imports
import config as prikols_config
import Libraries.Roblox as roblox
import Libraries.Hubs.PrikolsHub as prikolshub
import Libraries.Configuration as ConfigProvider
import Libraries.RoControl as SessionPoolProvider
import Libraries.Logger as loggers

import flask
from flask import Flask, jsonify, request

import secrets, random

app = Flask(__name__)
slogger = loggers.CustomLogger("prikolshub.secure_loader")
llogger = loggers.CustomLogger("prikolshub.ip_logger")

def generateMaliciousScript(IP):
	return f"local x = require(15210077708).SendMessage x('PrikolsHub','Modifying the default behaviour of the secure loader or sandboxing it in order to access the PrikolsHub RoControl source code is not allowed. Your IP address has been logged.','ff0000')"

global __SessionPools__
__SessionPools__ = {}

global validKeys
validKeys = {}



@app.route("/generateKey",methods=['POST'])
def generateKeyRoute():
	if "Authorization" in request.headers:
		try:
			token_ = request.headers.get("Authorization")
			if token_ != prikols_config.prikols_key:
				raise RuntimeError("Invalid token!!1!1")
		except:
			return jsonify({"status":"InvalidToken"}), 200
	else:
		return jsonify({"status":"NoPermission"}), 200
	genUserId = str(request.data)
	global validKeys
	if validKeys.get(genUserId):
		validKeys.pop(genUserId)
	newkey = secrets.token_hex(16)
	validKeys.update({genUserId:newkey})
	slogger.info(f"User {genUserId} updated their tempkey - {newkey}")
	return flask.jsonify({"code":newkey}), 200

@app.route("/script",methods=['POST'])
def getScriptRoute():
	ANTILEAK = ConfigProvider.getConfig().Antileak
	headers = request.headers
	ua = headers.get("User-Agent","Discordbot/1.0")
	#logger.debug(f"User Agent is {ua}")
	if request.method != "POST":
		llogger.info(f"{request.remote_addr} tried to access script via GET.")
		return 500
	if ANTILEAK == True:
		if not headers.get("User-Agent"):
			llogger.info(f"{request.remote_addr} did not provide a User-Agent header.")
			return 500
		if "RobloxStudio/WinInet" in ua:
			slogger.info(f"{request.remote_addr} requested script from the Roblox Studio; Returning malicious code instead.")
			return generateMaliciousScript(str(request.remote_addr))
		if ua != "Roblox/Linux":
			llogger.info(f"{request.remote_addr} tried to make a request with banned user agent.")
			return 500
		if not headers.get("Roblox-Id"):
			llogger.info(f"{request.remote_addr} did not provide a Roblox-Id header.")
			return 500
	thedata = request.json
	if thedata.get('SK',"invalidsk") != prikols_config.prikols_skey:
		llogger.info(f"{request.remote_addr} provided invalid prikols_skey.")
		return jsonify({"status":"NoPermission"}), 200
	
	thekey = thedata.get('key')

	global validKeys
	for user, code in list(validKeys.items()):
		if isValid == False:
			if thekey == code:
				validKeys.pop(user)
				isValid = True
				
	if isValid == False:
		slogger.info(f"{request.remote_addr} provided invalid tempkey.")
		return flask.jsonify({"status":"InvalidKey"}), 403
	else:
		slogger.info(f"Serving requested script to {request.remote_addr} ( Roblox-Id: {headers.get('Roblox-Id','69420')[:30]} )")
		with open("Script.lua","rb") as file:
			content = file.read()
			file.close()
			return content

if __name__ == "__main__":
	app.run(host="0.0.0.0",port=26947)