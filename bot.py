# PrikolsHub Imports
import config as prikols_config
import Libraries.Roblox as roblox
import Libraries.Hubs.PrikolsHub as prikolshub
import Libraries.Configuration as ConfigProvider
import Libraries.RoControl as SessionPoolProvider
import Libraries.Logger as loggers # import getLogger, prikols_logger, splogger
from Libraries.Sync import Sync, SyncPools

import discord, secrets, random, typing, os
from discord.ext import tasks
from discord import app_commands
from discord import ui

global guild
guild: discord.Guild = None

async def notifyUser(userId:int,message:str,embed:discord.Embed=None,view:discord.ui.View=None):
	try:
		await guild.get_member(userId).send(message,embed=embed,view=view)
	except:
		pass

intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

logger = loggers.prikols_logger # logger.getLogger("prikolshub")
splogger = loggers.splogger # logger.getLogger("prikolshub.session_pool")

config = ConfigProvider.getConfig()

@client.event
async def on_interaction(interaction: discord.Interaction):
	if interaction.is_expired():
		await interaction.response.send_message("The interaction collector for this message has expired. Rerun the command.",ephemeral=True)

global session_pools
session_pools = {}

def getSessionPoolById(id:int):
	return [ session_pools.get(pool) for pool in session_pools if session_pools.get(pool).sespool_id == id ][0]

async def sessionPoolAutocomplete(interaction:discord.Interaction,current:str) -> typing.List[app_commands.Choice[str]]:
	return [
		app_commands.Choice(name=session_pools.get(pool).sespool_name,value=session_pools.get(pool).sespool_id) for pool in session_pools if current.lower() in session_pools.get(pool).sespool_name.lower()
	]

@tree.command(name="autocomplete_test",description="do not use")
@app_commands.autocomplete(session_pool=sessionPoolAutocomplete)
async def autocomplete_test(interaction:discord.Interaction,session_pool:int):
	try:
		await interaction.response.send_message(getSessionPoolById(session_pool).sespool_name)
	except Exception as ex:
		await interaction.response.send_message(ex)

def getSessionPools():
	return session_pools

@client.event
async def on_message(message:discord.Message):
	#if message.guild != prikols_config.guild:
	#	return
	sp: SessionPoolProvider.SessionPool = session_pools.get(str(message.channel.id),False)
	if sp == False:
		return
	try:
		if len(message.content) == 0:
			return
		if message.author.bot == True:
			if message.author.id == 1101814904471695380:
				pass
			elif message.author.id == 974297735559806986: # GenAi
				pass
			else:
				return

		col = f'{message.author.color.value:X}'
		if len(col) != 6: 
			col = 'FF0000'
		member_name = message.author.display_name or message.author.name
		if message.author.get_role(prikols_config.ANONYMOUSROLE_ID):
			member_name = "PrikolsHub"
			col = 'FF0000'
		sp.RegisterChatMessage(member_name,col,message.content)
	except:
		pass

async def debugInfoAutocomplete(interaction:discord.Interaction,current:str) -> typing.List[app_commands.Choice[str]]:
	return [
		app_commands.Choice(name="SessionPool information",value=1),
		app_commands.Choice(name="Session request queue",value=2)
	]

@tree.command(name="debug",description="Get useful debugging information. DO NOT USE")
@app_commands.describe(infotype="Information type to return")
@app_commands.autocomplete(infotype=debugInfoAutocomplete)
async def sespool_debug(interaction:discord.Interaction,infotype:int):
	if interaction.user.id in prikols_config.owners:
		pass
	else:
		await interaction.response.send_message("You are not the owner of PrikolsHub RoControl!",ephemeral=True)
		return
	
	if infotype == 1:
		sp: SessionPoolProvider.SessionPool = session_pools.get(str(interaction.channel_id),False)
		if sp == False:
			await interaction.response.send_message("sessionpool doesnt exist")
			return
		cach = sp.GetDebuggingInformation()
		await interaction.response.send_message(f"PrikolsHub SessionPool Debug\n```json\n{ConfigProvider.json.dumps(cach)}\n```",ephemeral=True)
		return

	if infotype == 2:
		synceddata = SyncPools("Test")
		#print(synceddata)
		await interaction.response.send_message(f"PrikolsHub Session Queue Debug\n```json\n{ConfigProvider.json.dumps(synceddata)}\n```",ephemeral=True)
		return
	
	await interaction.response.send_message(f"Invalid information type",ephemeral=True)

async def LoadSessionPools():
	"""
	Implementation to load all of the session pools in `db/session_pools.json`
	"""
	global session_pools
	session_pools_cache = []
	with open("db/session_pools.json","r") as file:
		session_pools_cache = ConfigProvider.json.loads(file.read()).get("SessionPools",[])
	for session_pool in session_pools_cache:
		splogger.info(f"Loading SessionPool {session_pool[0]} (ID: {session_pool[1]})")
		
		ch = guild.get_channel(session_pool[1])
		the_webhook = None
		for webhook in await ch.webhooks():
			if webhook.name == "PrikolsHub RoControl SessionPool":
				the_webhook = webhook
		if not the_webhook:
			loggers.splogger.info(f"Creating webhook in {session_pool[0]} (ID: {session_pool[1]})")
			the_webhook = await ch.create_webhook(name="PrikolsHub RoControl SessionPool")

		thepool = SessionPoolProvider.SessionPool(name=session_pool[0],persistkey=session_pool[2],channel=ch,webhook=the_webhook)
		#thepool.AddServer("ffffffff-ffff-ffff-ffffffffffff",69420)
		#thepool.SendRobloxMessageToChannel("OCboy3","OCbwoy3",1083030325,f"test message session pool {session_pool[0]}","ffffffff-ffff-ffff-ffffffffffff",69420)
		#thepool.RemoveServer("ffffffff-ffff-ffff-ffffffffffff",69420)

		session_pools.update({str(session_pool[1]):thepool})
	loggers.CustomLogger("prikolshub.debugger").debug("SessionPools: "+str(session_pools))

@tasks.loop(seconds=1,count=None)
async def serverUpdateLoop():
	synced = SyncPools()
	tad = synced.get("create",[])
	trm = synced.get("remove",[])
	for obj in tad:
		try:
			xd = obj[1].split("@")
			getSessionPoolById(int(obj[0])).AddServer(xd[0],int(xd[1]))
		except:
			pass
	for obj in trm:
		try:
			xd = obj[1].split("@")
			getSessionPoolById(int(obj[0])).RemoveServer(xd[0],int(xd[1]))
		except:
			pass

@tasks.loop(seconds=5,count=None)
async def statusChangeLoop():
	connected_servers = 0
	for sessionpool in session_pools:
		connected_servers += len(session_pools.get(sessionpool,{"servers":[]}).servers)
	skw,spkw = "servers", "SessionPools"
	if connected_servers == 1:
		skw = "server"
	if len(session_pools) == 1:
		spkw = "SessionPool" 
	rstat = discord.Activity(type=discord.ActivityType.watching,name=f"{connected_servers} {skw} in {len(session_pools)} {spkw}.")
	await client.change_presence(activity=rstat,status=prikols_config.status)


@client.event
async def on_ready():
	logger.info(f"Successfully logged in as {client.user.name}#{client.user.discriminator}")
	global guild
	guild = client.get_guild(prikols_config.guild)
	statusChangeLoop.start()

	import Libraries.Extensions.OwnerCommands as OwnerGroup
	OwnerGroup.BOT_CLIENT = client
	OwnerGroup.config = ConfigProvider
	OwnerGroup.getSessionPoolsFunc = getSessionPools

	tree.add_command(OwnerGroup.OwnerGroup(name="owner",description="Contains Owner-Only commands."))

	await tree.sync()

	logger.info("Loading SessionPools")

	#NOTE - DO NOT REMOVE THESE TWO
	await LoadSessionPools()
	serverUpdateLoop.start()

	logger.info("Successfully loaded!")

def runBot():
	logger.info("PrikolsHub RoControl MultiSession v1 d87f31a")
	client.run(prikols_config.token)

if __name__ == "__main__":
	runBot()