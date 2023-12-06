# PrikolsHub Imports
import config as prikols_config
import Libraries.Roblox as roblox
import Libraries.Hubs.PrikolsHub as prikolshub
from Libraries.Logger import getLogger

import discord, secrets, random, typing, os
from discord.ext import tasks
from discord import app_commands
from discord import ui

global guild
guild: discord.Guild = None

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

logger = getLogger("prikolshub")

async def notifyUser(userId:int,message:str,embed:discord.Embed=None,view:discord.ui.View=None):
	try:
		await guild.get_member(userId).send(message,embed=embed,view=view)
	except:
		pass

@client.event
async def on_interaction(interaction: discord.Interaction):
	pass

@client.event
async def on_message(message:discord.Message):
	pass

# TODO: Implement the actual main part of PrikolsHub RoControl

@client.event
async def on_ready():
	logger.info(f"Successfully logged in as {client.user.name}#{client.user.discriminator}")
	global guild
	guild = client.get_guild(prikols_config.guild)

	import Libraries.Extensions.OwnerCommands as OwnerGroup
	OwnerGroup.BOT_CLIENT = client
	tree.add_command(OwnerGroup.OwnerGroup(name="owner",description="Contains Owner-Only commands."))

	@tasks.loop(seconds=5,count=None)
	async def statusChangeLoop():
		rstat = random.choice(prikols_config.statuses)
		await client.change_presence(activity=rstat,status=prikols_config.status)

	statusChangeLoop.start()

	await tree.sync()
	logger.info("Successfully loaded!")

def runBot():
	logger.info("PrikolsHub RoControl MultiSession v1 d87f31a")
	client.run(prikols_config.token)

if __name__ == "__main__":
	runBot()