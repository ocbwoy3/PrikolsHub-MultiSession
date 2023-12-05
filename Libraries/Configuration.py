import os, json, secrets
import Libraries.Util as util

ConfigUpdated = util.Event()

Default_Config = {
	"CensorProfanity":False,
	"PersistKey":secrets.token_urlsafe(128),
	"EnablePersistKey":False,
	"KillSwitch":False
}

os.makedirs('db',exist_ok=True)

def integrityCheck():
	os.makedirs('db',exist_ok=True)
	if 'config.json'in os.listdir("db"):
		with os.open('db/config.json','w') as file:
			try:
				json.loads(file.read())
			except:
				file.write(json.dumps(Default_Config))
			file.close()
	else:
		with os.open('db/config.json','w') as file:
			file.write(json.dumps(Default_Config))
			file.close()
		ConfigUpdated.Trigger(Default_Config)

def UpdateConfig(new_config):
	os.makedirs('db',exist_ok=True)
	if 'config.json'in os.listdir("db"):
		pass
	with os.open('db/config.json','w') as file:
		file.write(json.dumps(new_config))
		file.close()
	ConfigUpdated.Trigger(new_config)

integrityCheck()