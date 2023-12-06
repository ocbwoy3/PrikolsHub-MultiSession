import os, json, secrets
import Libraries.Util as util

from Libraries.Logger import getLogger

sclogger = getLogger("prikolshub.config")
ilogger = getLogger("prikolshub.integrity")


ConfigUpdated = util.Event()

Default_Config = {
	"CensorProfanity":False,
	"EnablePersistKey":False,
	"KillSwitch":False,
	"AllowExeCommand":True
}

Config_l10n = {
	"CensorProfanity":"Censor Profanity",
	"EnablePersistKey":"Enable usage of PERSISTKEY",
	"KillSwitch":"Kill Switch",
	"AllowExeCommand":"Allow execution of user scripts"
}

def __integrityFieldCheck__(tbl):
	if len(tbl) != len(Default_Config):
		raise RuntimeError("Field amount mismatch")
	return tbl

global CURRENT_CONFIG_TEMP
CURRENT_CONFIG_TEMP = Default_Config

def __OnTempConfigUpdate__(new_config):
	global CURRENT_CONFIG_TEMP
	CURRENT_CONFIG_TEMP = new_config

ConfigUpdated.Subscribe(__OnTempConfigUpdate__)

def getConfig():
	os.makedirs('db',exist_ok=True)
	with open('db/config.json','r',encoding='utf-8') as file:
		try:
			new_conf = __integrityFieldCheck__(json.loads(file.read()))
			ConfigUpdated.Trigger(new_conf)
			file.close()
			return new_conf
		except Exception as ex:
			ilogger.warn("Integrity check failed")
			file.close()
			with open('db/config.json','w',encoding='utf-8') as file:
				file.write(json.dumps(Default_Config))
				ConfigUpdated.Trigger(Default_Config)
		return Default_Config
	
def UpdateConfig(new_config):
	os.makedirs('db',exist_ok=True)
	if 'config.json'in os.listdir("db"):
		pass
	with open('db/config.json','w',encoding='utf-8') as file:
		file.write(json.dumps(new_config))
		file.close()
	ConfigUpdated.Trigger(new_config)
	sclogger.info("configuration updated")

integrityCheck = getConfig

integrityCheck()