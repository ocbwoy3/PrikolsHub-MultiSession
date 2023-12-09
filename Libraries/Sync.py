import requests, flask
import Libraries.Util as util

import json
import config as prikols_config
from flask import Flask, jsonify, request

GetQueue = None

OnSync = util.Event()

def Sync(data):
	return requests.post(f"http://127.0.0.1:26947/sync/data",json.dumps(data),headers=prikols_config.HEADERS).json()

def SyncPools():
	return requests.post(f"http://127.0.0.1:26947/sync/pools","{}",headers=prikols_config.HEADERS).json()

def InitSyncServer(app:Flask):
	@app.route("/sync/data",methods=['POST'])
	def syncPath():
		if "Authorization" in request.headers:
			try:
				token_ = request.headers.get("Authorization")
				if token_ != prikols_config.prikols_key:
					raise RuntimeError("Invalid token!!1!1")
			except:
				return jsonify({"status":"InvalidToken"}), 200
		else:
			return jsonify({"status":"NoPermission"}), 200
		OnSync.Trigger(request.json)
		return jsonify({"status":"success"}), 200
			