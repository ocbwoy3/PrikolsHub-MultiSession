# PrikolsHub Imports
import config as prikols_config
import Libraries.Roblox as roblox
import Libraries.Hubs.PrikolsHub as prikolshub
import Libraries.Configuration as ConfigProvider
import Libraries.RoControl as SessionPoolProvider
import Libraries.Logger as loggers
import Libraries.Sync as Sync

import threading
import websockets, asyncio

import flask
from flask import Flask, jsonify, request

import secrets, random, copy

app = Flask(__name__)

Sync.InitSyncServer(app)
OnSync = Sync.OnSync

plogger = loggers.CustomLogger("prikolshub")
clogger = loggers.CustomLogger("prikolshub.config")
slogger = loggers.CustomLogger("prikolshub.secure_loader")
llogger = loggers.CustomLogger("prikolshub.ip_logger")
splogger = loggers.CustomLogger("prikolshub.session_pool")

def generateMaliciousScript(IP):
	"""
	# Do not let them access the code!
	`chapel1337`,
	`nebunet`,
	`JKeepWasHere`,
	`115`,
	`Skid World` & others.
	"""
	return f"local x = require(15210077708).SendMessage x('PrikolsHub','Accessing the PrikolsHub RoControl source code is not allowed. Your IP address has been forwarded to our Discord server and it will be used by 3rd parties accordingly. Adios, {IP}!','ff0000') -- nice try skid"

global __SessionPools__
__SessionPools__ = {}

def getSessionPoolById(id:int):
	return [ __SessionPools__.get(pool) for pool in __SessionPools__ if __SessionPools__.get(pool).sespool_id == id ][0]

def LoadSessionPools():
	global __SessionPools__
	session_pools_cache = []
	with open("db/session_pools.json","r") as file:
		session_pools_cache = ConfigProvider.json.loads(file.read()).get("SessionPools",[])
	for session_pool in session_pools_cache:
		splogger.info(f"Loading SessionPool {session_pool[0]} (ID: {session_pool[1]})")
		thepool = SessionPoolProvider.ServerSessionPool(name=session_pool[0],persistkey=session_pool[2])
		__SessionPools__.update({str(session_pool[1]):thepool})

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
	
	genUserId = str(request.json.get("user"))
	genPool = str(request.json.get("pool"))

	global validKeys
	
	if validKeys.get(genUserId):
		validKeys.pop(genUserId)
	
	newkey = secrets.token_hex(16)
	newdata = {"key":newkey,"pool":genPool}
	
	validKeys.update({genUserId:newdata})
	slogger.info(f"User {genUserId} updated their tempkey for {getSessionPoolById(int(genPool)).sespool_name} - {newkey}")
	
	return ConfigProvider.json.dumps({"code":newkey}), 200

def generateScriptPrefix(sessionpool_id:int):
	return f"-- bro thinks he can leak the source code\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nlocal PRIKOLS_SESPOOL_ID={sessionpool_id} local PRIKOLS_SESPOOL_KEY='{getSessionPoolById(sessionpool_id).persistkey}'"
	
# Script format:
# local actions = "{}" pcall(get_actions) local prikols_sk, prikols_spname = "super secret key i dont want you to know about", "SessionPool"
# -- script goes here

@app.route("/script",methods=['POST'])
def getScriptRoute():
	ANTILEAK = ConfigProvider.getConfig().get('Antileak',True)
	
	headers = request.headers
	ua = headers.get("User-Agent","Discordbot/1.0")

	if ANTILEAK == True:
		if not headers.get("User-Agent"):
			llogger.info(f"{request.remote_addr} did not provide a User-Agent header.")
			jsonify({"status":"NotFound"}), 404
		
		if "RobloxStudio/WinInet" in ua:
			slogger.info(f"{request.remote_addr} requested script from the Roblox Studio; Returning malicious code instead.")
			return generateMaliciousScript(str(request.remote_addr))
		
		if ua != "Roblox/Linux":
			llogger.info(f"{request.remote_addr} tried to make a request with banned user agent.")
			jsonify({"status":"NotFound"}), 404
		
		if not headers.get("Roblox-Id"):
			llogger.info(f"{request.remote_addr} did not provide a Roblox-Id header.")
			jsonify({"status":"NotFound"}), 404
		
	thedata = request.json
	
	if thedata.get('SK',"invalidsk") != prikols_config.prikols_skey:
		llogger.info(f"{request.remote_addr} provided invalid prikols_skey.")
		return jsonify({"status":"NoPermission"}), 200
	
	thekey = thedata.get('key')

	global validKeys
	
	thekeytouse = None
	for user, code in list(validKeys.items()):
		if isValid == False:
			if thekey == code.get("key"):
				thekeytouse = copy.deepcopy(code)
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
			prefix = generateScriptPrefix(int(thekeytouse.get("pool")))
			return prefix + "\n" + content

@app.route("/",methods=['GET'])
def getRoot():
	return {"Name":"PrikolsHub RoControl MultiSession","SessionPools":len(__SessionPools__)}

global sessionsQueuedForCreation
sessionsQueuedForCreation = []

global sessionsQueuedForRemoval
sessionsQueuedForRemoval = []

def getImportantStuff():
	global sessionsQueuedForCreation, sessionsQueuedForRemoval
	qcr = copy.deepcopy(sessionsQueuedForCreation)
	qrm = copy.deepcopy(sessionsQueuedForRemoval)
	sessionsQueuedForCreation = []
	sessionsQueuedForRemoval = []
	return {
		"create":qcr,
		"remove":qrm
	}

@app.route("/sync/pools",methods=['POST'])
def syncPathPools():
	if "Authorization" in request.headers:
		try:
			token_ = request.headers.get("Authorization")
			if token_ != prikols_config.prikols_key:
				raise RuntimeError("Invalid token!!1!1")
		except:
			return jsonify({"status":"InvalidToken"}), 200
	else:
		return jsonify({"status":"NoPermission"}), 403
	return getImportantStuff()

@app.route("/pool/<pool>/<session>/create",methods=["POST"])
def createSession(pool:str,session:str):
	sp: SessionPoolProvider.ServerSessionPool = getSessionPoolById(int(pool[:3]))
	if not sp:
		return jsonify({"status":"SessionPoolNotFound"}), 404
	splitted = session.split("@")
	if len(splitted) != 2:
		return jsonify({"status":"NotFound"}), 404
	try:
		sp.AddServer(splitted[0],int(splitted[1]))
		global sessionsQueuedForCreation
		sessionsQueuedForCreation.append([pool[:5],session[:50]])
		return jsonify({"staus":"success","name":sp.sespool_name}), 200
	except:
		return jsonify({"staus":"exists"}), 403

@app.route("/pool/<pool>/<session>/remove",methods=["POST"])
def removeSession(pool:str,session:str):
	sp: SessionPoolProvider.ServerSessionPool = getSessionPoolById(int(pool[:3]))
	if not sp:
		return jsonify({"status":"SessionPoolNotFound"}), 404
	splitted = session.split("@")
	if len(splitted) != 2:
		return jsonify({"status":"NotFound"}), 404
	try:
		sp.RemoveServer(splitted[0],int(splitted[1]))
		global sessionsQueuedForRemoval
		sessionsQueuedForRemoval.append([pool[:5],session[:50]])
		return jsonify({"staus":"success"}), 200
	except:
		return jsonify({"staus":"doesntexist"}), 403

@app.route("/in/<pool>/m",methods=["POST"])
def poolGetQueueEndpoint(pool:str):
	if "Authorization" in request.headers:
		try:
			token_ = request.headers.get("Authorization")
			if token_ != prikols_config.prikols_key:
				raise RuntimeError("Invalid token!!1!1")
		except:
			raise RuntimeError("idk")
	else:
		return jsonify({"status":"NoPermission"}), 403
	#print(pool)
	sp: SessionPoolProvider.ServerSessionPool = getSessionPoolById(int(pool))
	#print(sp.sespool_name)
	#print(request.headers,bytes(request.data),request.json)
	if not sp:
		return jsonify({}), 404
	try:
		for msg in request.json.get('messages'):
			sp.SendToRoblox(msg)
		if not sp:
			return jsonify({"status":"SessionPoolNotFound"}), 404
		return jsonify({"cache":sp.GetRobloxCache()}), 200
	except Exception as ex:
		print(ex)
		return "{}"

@app.route("/pool/<pool>/<session>/messages",methods=["POST"])
def getMessagesEndpoint(pool:str,session:str):
	sp: SessionPoolProvider.ServerSessionPool = getSessionPoolById(int(pool[:3]))
	if not sp:
		return jsonify({"status":"SessionPoolNotFound"}), 404
	if not session[:50] in sp.servers:
		return jsonify({"status":"ServerNotFound"}), 404
	print(request.json)
	for msg in request.json.get('messages'):
		sp.SendToDiscord(msg)
	splittedsession = session.split('@')
	return jsonify({"cache":sp.GetSessionCache(splittedsession[0],int(splittedsession[1]))}), 200

if __name__ == "__main__":
	DisableWerkzeugLogger = ConfigProvider.getConfig().get('DisableWerkzeugLogger',True)
	if DisableWerkzeugLogger == True:
		loggers.logging.getLogger('werkzeug').disabled = True
		app.logger.disabled = True
		clogger.info("Disabed werkzeug logger")
	LoadSessionPools()
	plogger.info("Starting flask server on port 26947. URL: http://127.0.0.1:26947")
	app.run(host="0.0.0.0",port=26947)