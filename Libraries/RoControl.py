"""
# SessionPoool
"""

import secrets, discord, copy
import Libraries.Roblox as roblox
import Libraries.Logger as loggers
from discord.ext import tasks

global __SessionPools__
__SessionPools__ = {}

global __SessionsCreated__
__SessionsCreated__ = 0

# From Discord
# [str,bool,array] - command

# From Roblox
# [str,int,str] - message

debug = loggers.CustomLogger("prikolshub.debugger")
splogger = loggers.splogger

class ServerSessionPool:
	ses_skey = "None"
	sespool_name = "Unknown SessionPool"
	sespool_id = -1

	persistkey = secrets.token_urlsafe(32)

	session_cache = {}
	roblox_cache = []
	servers = []

	def __init__(self,name:str,persistkey=secrets.token_urlsafe(32)):
		global __SessionsCreated__
		global __SessionPools__
		__SessionsCreated__ += 1
		self.sespool_id = __SessionsCreated__
		self.sespool_name = name
		self.ses_skey = secrets.token_urlsafe(16)
		self.persistkey = persistkey

	def SendToRoblox(self,thing_to_send):
		for session in self.session_cache.keys():
			self.session_cache.get(session).append(thing_to_send)

	def SendToDiscord(self,thing_to_send):
		self.roblox_cache.append(thing_to_send)

	def AddServer(self,jobid:str,placeid:int):
		self.servers.append(f"{jobid[:50]}@{str(placeid)[:50]}")
		self.session_cache.update({f"{jobid[:50]}@{str(placeid)[:50]}":[]})
		splogger.info(f"Server {jobid[:50]}@{str(placeid)[:50]} added to {self.sespool_name}")

	def RemoveServer(self,jobid:str,placeid:int):
		try:
			self.servers.pop(f"{jobid[:50]}@{str(placeid)[:50]}")
			self.session_cache.pop(f"{jobid[:50]}@{str(placeid)[:50]}","")
		except:
			pass
		splogger.info(f"Server {jobid[:50]}@{str(placeid)[:50]} removed from {self.sespool_name}")

	def GetSessionCache(self,jobid:str,placeid:int):
		tr = copy.deepcopy(self.session_cache.get(f"{jobid[:50]}@{str(placeid)[:50]}",[]))
		self.session_cache.update({f"{jobid[:50]}@{str(placeid)[:50]}":[]})
		return tr
	
	def GetRobloxCache(self):
		tr = copy.deepcopy(self.roblox_cache)
		self.roblox_cache = []
		return tr

	def GetDebuggingInformation(self):
		return {
			"session_cache": self.session_cache,
			"roblox_cache": self.roblox_cache,
			"servers": self.servers,
			"name": self.sespool_name,
			"id": self.sespool_id
		}


class SessionPool:
	ses_skey = "None"
	sespool_name = "Unknown SessionPool"
	sespool_id = -1

	persistkey = secrets.token_urlsafe(32)

	session_cache = {}
	romsg_cache = []
	servers = []

	pfp_cache = {}

	channel: discord.TextChannel = None
	webhook: discord.Webhook = None

	def __init__(self,name:str,persistkey=secrets.token_urlsafe(32),channel:discord.TextChannel=None,webhook=discord.Webhook):
		global __SessionsCreated__
		global __SessionPools__
		__SessionsCreated__ += 1
		self.sespool_id = __SessionsCreated__
		self.sespool_name = name
		self.ses_skey = secrets.token_urlsafe(16)
		self.persistkey = persistkey
		self.channel = channel
		self.webhook = webhook

	def AddServer(self,jobid:str,placeid:int):
		emb = discord.Embed(
			color = discord.Color.from_rgb(0,255,0),
			title="Server connected",
			description=f"Place ID: {str(placeid)[:50]}\nJob ID: {jobid[:50]}\nSession Pool: {self.sespool_name}"
		)
		@tasks.loop(count=1,seconds=0.001)
		async def postMsg():
			await self.channel.send(embed=emb)
		postMsg.start()
		splogger.info(f"Server {jobid[:50]}@{str(placeid)[:50]} added to {self.sespool_name}")
		self.servers.append(f"{jobid[:50]}@{str(placeid)[:50]}")
		self.session_cache.update({f"{jobid[:50]}@{str(placeid)[:50]}":[]})

	def RemoveServer(self,jobid:str,placeid:int):
		try:
			self.servers.pop(f"{jobid[:50]}@{str(placeid)[:50]}")
			self.session_cache.pop(f"{jobid[:50]}@{str(placeid)[:50]}","")
		except:
			pass
		emb = discord.Embed(
			color = discord.Color.from_rgb(255,0,0),
			title="Server disconnected",
			description=f"Job ID: {jobid[:50]}\nSession Pool: {self.sespool_name}"
		)
		@tasks.loop(count=1,seconds=0.001)
		async def postMsg():
			await self.channel.send(embed=emb)
		postMsg.start()
		splogger.info(f"Server {jobid[:50]}@{str(placeid)[:50]} removed from {self.sespool_name}")

	def RegisterCommandUse(self,commandName:str,arguments:[str]):
		for session in self.session_cache.keys():
			self.session_cache.get(session).append([commandName,True,arguments])

	def RegisterChatMessage(self,sender:str,role_color:str,message:str):
		#print(sender,role_color,message)
		for session in self.session_cache.keys():
			self.session_cache.get(session).append([sender,role_color,message[:500]])

	def SendRobloxMessageToChannel(self,name:str,display_name:str,user_id:int,message:str,jobid:str,placeid:int):
		if f"{jobid[:50]}@{str(placeid)[:50]}" not in self.servers:
			#debug.debug(f"JobID {jobid} tried to send message but is not in servers!")
			return
		pfp = self.pfp_cache.get(str(user_id),False)
		if pfp == False:
			pfp = roblox.getProfilePic(user_id)
			self.pfp_cache.update({str(user_id):pfp})
		@tasks.loop(count=1,seconds=0.001)
		async def postMsg():
			the_message = message.replace("&lt;","\<").replace("&gt;","\>").replace("&amp;","\&").replace("&apos;","\\'").replace("&quot;","\\\"")
			if '$' in name:
				await self.webhook.send(the_message[:500],username=f"{display_name}",avatar_url=pfp)
			else:	
				await self.webhook.send(the_message[:500],username=f"{display_name} (@{name}, {user_id}, {jobid[:50]}@{str(placeid)[:50]})",avatar_url=pfp)
		postMsg.start()
		
	def GetSessionCache(self,jobid:str,placeid:int):
		tr = copy.deepcopy(self.session_cache.get(f"{jobid[:50]}@{str(placeid)[:50]}",[]))
		self.session_cache.update({f"{jobid[:50]}@{str(placeid)[:50]}":[]})
		return tr

	def GetDebuggingInformation(self):
		return {
			"session_cache": self.session_cache,
			"servers": self.servers,
			"pfp_cache": self.pfp_cache,
			"name": self.sespool_name,
			"id": self.sespool_id
		}