"""
# Owner Commands
"""

import config as prikols_config
import discord
from discord import app_commands
import os

import json

import Libraries.Logger as logger
alogger = logger.getLogger("prikolshub.archiver")
sjlogger = logger.getLogger("prikolshub.settings")

def parseFileExtension(filename:str):
	fn, file_extension = os.path.splitext(filename)
	return file_extension

def getPFPThingy(message:discord.Message):
	return str(message.author.id)+"-w"+str(message.author.display_name.__hash__()).replace("-","b")

BOT_CLIENT:discord.Client = None

class OwnerGroup(app_commands.Group):
	BOTCLIENT = BOT_CLIENT

	@app_commands.command(name="killswitch",description="Disable the usage of the /script command to the general public.")
	@app_commands.describe(enable="The state of the script command.")
	async def killswitchCommand(self,interaction:discord.Interaction,enable:bool):
		if interaction.user.id in prikols_config.owners:
			pass
		else:
			await interaction.response.send_message("You are not the owner of PrikolsHub RoControl!",ephemeral=True)
			return
		await interaction.response.send_message("Attempting to set!",ephemeral=True)
		global SCRIPT_KILLSWITCH
		SCRIPT_KILLSWITCH = enable
	
	@app_commands.command(name="export",description="Exports the current channel alongside it's media into a folder.")
	async def exportCommand(self,interaction:discord.Interaction):
		if interaction.user.id in prikols_config.owners:
			pass
		else:
			await interaction.response.send_message("You are not the owner of PrikolsHub RoControl!",ephemeral=True)
			return
	
		await interaction.response.defer(thinking=True,ephemeral=False)
		alogger.info(f"Archiving #{interaction.channel.name} ({interaction.channel_id})")
		try:
			os.makedirs("channels",exist_ok=True)
			os.makedirs("media",exist_ok=True)
			os.makedirs(f"media/{interaction.channel_id}",exist_ok=True)
	
			alogger.debug(f"Getting channel history of {interaction.channel_id}")
			messages = []
			saved_pfps = {}
			async for message in interaction.channel.history(oldest_first=True,limit=None):
				messages.append([
					message.created_at.__str__(),
					message.author.display_name or message.author.name,
					getPFPThingy(message),
					str(message.content),
					[[attachment.id,attachment.filename,attachment.content_type] for attachment in message.attachments]
				])
				if saved_pfps.get(str(getPFPThingy(message)),False) == False:
					saved_pfps.update({str(getPFPThingy(message)):True})
					try:
						await message.author.display_avatar.save(f"media/{interaction.channel_id}/pfp-{getPFPThingy(message)}.png")
						alogger.info(f"Saved PFP of {message.author.name} ({message.author.id})")
					except:
						alogger.info(f"Cannot save PFP of {message.author.name} ({message.author.id})")
				for attachment in message.attachments:
					try:
						await attachment.save(f"media/{interaction.channel_id}/attachment-{attachment.id}{parseFileExtension(attachment.filename)}")
						alogger.info(f"Saved message attachment {attachment.filename} ({attachment.id})")
					except:
						alogger.info(f"Failed to save message attachment {attachment.filename} ({attachment.id})")
			dataToSave = {
				"channel-name":interaction.channel.name,
				"id":interaction.channel_id,
				"topic":interaction.channel.topic,
				"nsfw":interaction.channel.nsfw,
				"messages":messages
			}
			#print(dataToSave)
			with open(f"channels/{interaction.channel_id}.json","w") as file:
				file.write(json.dumps(dataToSave))
				file.close()
				alogger.info(f"Channel contents channels/{interaction.channel_id}.json, media and pfps saved to media/{interaction.channel_id}")
			await interaction.followup.send(f":white_check_mark: Successfully archived channel")
		except Exception as ex:
			try:
				await interaction.followup.send(f":octagonal_sign: {ex.__class__.__name__}: {ex}")
			except:
				await interaction.followup.send(":octagonal_sign: Unknown Error")
	
	@app_commands.command(name="say",description="Say stuff")
	@app_commands.describe(message="Something you would like so say")
	async def chatMsg(self,interaction:discord.Interaction,message:str):
		if interaction.user.id in prikols_config.owners:
			pass
		else:
			await interaction.response.send_message("You are not the owner of PrikolsHub RoControl!",ephemeral=True)
			return
		await interaction.response.send_message("Sent",ephemeral=True)
		await interaction.channel.send(message)

	@app_commands.command(name="impersonate",description="Impersonates a user by stealing their profile details.")
	@app_commands.describe(victim="The victim the bot is going to impersonate.",username="Manually asign a username.")
	async def impersonateCommand(self,interaction:discord.Interaction,victim:discord.User,username:str=None):
		if interaction.user.id in prikols_config.owners:
			pass
		else:
			await interaction.response.send_message("You are not the owner of PrikolsHub RoControl!",ephemeral=True)
			return
		try:
			await interaction.guild.get_member(self.BOTCLIENT.user.id).edit(nick=victim.display_name)
			victim_avatar = await victim.display_avatar.read()
			theuser = username or victim.display_name
			await self.BOTCLIENT.user.edit(avatar=victim_avatar,username=theuser)
			await interaction.response.send_message(f"Successfully impersonated <@{victim.id}>!",ephemeral=True)
			logger.info(f"Impersonation command got triggered. User impersonated: {victim.display_name} (@{victim.name})")
		except Exception as ex:
			try:
				try:
					victim_avatar = await victim.display_avatar.read()
					await self.BOTCLIENT.user.edit(avatar=victim_avatar)
					await interaction.response.send_message(f"Partially impersonated <@{victim.id}>!\nException: {ex}",ephemeral=True)
					logger.warning("Only PFP got updated, possibly due to rate limiting.")
				except Exception as ex2:
					logger.error("Nothing updated, possibly due to rate limiting.")
					await interaction.response.send_message(f"FallbackPFPUpdateOnly - Report exception to OCbwoy3: {ex2}",ephemeral=True)
			except:
				await interaction.response.send_message(f"impersonateFailDisplay - Report exception to OCbwoy3: Failed to display exception",ephemeral=True)
