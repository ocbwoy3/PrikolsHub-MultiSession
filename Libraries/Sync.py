import requests, flask
import Libraries.Util as util

import config as prikols_config
from flask import Flask, jsonify, request

OnSync = util.Event()

def sync(data):
	return requests.post(f"http://127.0.0.1:26947/sync",data,headers=prikols_config.HEADERS).json

def InitSyncServer(app:Flask):
	@app.route("/sync",methods=['POST'])
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