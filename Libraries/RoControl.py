"""
# SessionPoool
"""

import secrets, discord, copy

global __SessionPools__
__SessionPools__ = {}

global __SessionsCreated__
__SessionsCreated__ = 0

# From Discord
# [str,str,str] - message
# [str,bool,array] - command

# From Roblox
# [str,int,str] - message

class SessionPool:
	ses_skey = "None"
	sespool_name = "Unknown SessionPool"
	sespool_id = -1

	session_cache = {}
	romsg_cache = []
	servers = []

	def __init__(self,name:str):
		__SessionsCreated__ += 1
		self.sespool_id = __SessionsCreated__
		self.sespool_name = name
		self.ses_skey = secrets.token_urlsafe(16)

	def AddServer(self,jobid:str):
		self.servers.append(str(jobid))
		self.session_cache.update({str(jobid):[]})

	def RemoveServer(self,jobid:str):
		try:
			self.servers.pop(jobid)
			self.session_cache.pop(jobid,"")
		except:
			pass

	def RegisterCommandUse(self,commandName:str,arguments:[]):
		for session in self.session_cache:
			session.append([commandName,True,arguments])

	def RegisterChatMessage(self,sender:str,role_color:str,message:str):
		for session in self.session_cache:
			session.append([sender,role_color,message])

	def GetSessionCache(self,jobid:str):
		tr = copy.deepcopy(self.session_cache.get(jobid,{}))
		self.session_cache.update({str(jobid):{}})
		return tr