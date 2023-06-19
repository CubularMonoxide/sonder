import discord # pip install py-cord
import json
import difflib
import re
import random as rnd
from datetime import datetime
from datetime import date
import time
import os
import rolldice # pip install py-rolldice
from func_timeout import func_timeout, FunctionTimedOut # pip install func-timeout

def log(msg):
	print(date.today(), datetime.now().strftime("| %H:%M:%S |"), msg)

log("Initializing...")
boot_time = int(time.time())

bot = discord.Bot(activity=discord.Game(name='FIST: Ultra Edition'))

log("Loading token")
token_file = open('token.json')
token_file_data = json.load(token_file)
ownerid = token_file_data["owner_id"]
token = token_file_data["token"]
token_file.close()

log("Loading traits")
trait_file = open('traits.json')
trait_data = json.load(trait_file)
trait_file.close()

trait_file = open('secret_trait.json')
secret_trait = json.load(trait_file)
trait_file.close()

log("Loading roles")
role_file = open('roles.json')
role_data = json.load(role_file)
role_file.close()

log("Creating role and trait name list")
trait_names = []
for trait in trait_data:
	trait_names.append(trait["Name"])

role_names = []
for role in role_data:
	role_names.append(role["Name"])

num_to_die = {
	1: "<:revolver_dice_1:1029946656277405726>",
	2: "<:revolver_dice_2:1029946657439223858>",
	3: "<:revolver_dice_3:1029946659087601714>",
	4: "<:revolver_dice_4:1029946660341690368>",
	5: "<:revolver_dice_5:1029946661541269554>",
	6: "<:revolver_dice_6:1029946662531113011>"
}

log("Defining helper functions")
def d6():
	return rnd.randint(1,6)

def trait_message_format(trait):
	return f"**{trait['Name']}** ({trait['Number']})\n{trait['Effect']}\n- {trait['Item']}, {trait['Stat']}"

def role_message_format(role):
	return f"**{role['Name']}** ({role['Number']})\n{role['Text']}"

def search_for_trait(trait):
	message = ""
	if re.match("^\d+$", trait):
		number = int(trait)
		message = "No trait exists with the given number. Trait numbers must be possible d666 roll outputs."
		for trait in trait_data:
			if trait["Number"] == number:
				message = trait_message_format(trait)
				break
	else:
		best_match = difflib.get_close_matches(trait.upper(), trait_names, n=1, cutoff=0.0)

		if len(best_match) > 0:
			goodtrait = {}
			for trait in trait_data:
				if trait["Name"] == best_match[0]:
					goodtrait = trait
					break
			message = trait_message_format(trait)
		else:
			message = "Could not find a trait with an approximately similar name."
	return message

def search_for_role(role):
	message = ""
	if re.match("^\d+$", role):
		number = int(role)
		message = "No role exists with the given number. Role numbers must be possible d66 roll outputs."
		for role in role_data:
			if role["Number"] == number:
				message = role_message_format(role)
				break
	else:
		best_match = difflib.get_close_matches(role.upper(), role_names, n=1, cutoff=0.0)

		if len(best_match) > 0:
			goodtrait = {}
			for role in role_data:
				if role["Name"] == best_match[0]:
					goodtrait = role
					break
			message = role_message_format(role)
		else:
			message = "Could not find a role with an approximately similar name."
	return message

def roll_intelligence_matrix(table):
	roll_type = table["Roll"].upper()
	if roll_type == "2D6":
		roll_result = d6() + d6()
		return table["Values"][str(roll_result)]
	else:
		return rnd.choice(list(table["Values"].values()))

def roll_all_matrices(table_list):
	out = []
	for table in table_list:
		out.append(roll_intelligence_matrix(table))
	return out
	
def decap_first(string):
	if len(string) > 1:
		if string[1].islower() or not string[1].isalpha():
			return string[0].lower() + string[1:]
	return string

def remove_duplicates(lst):
	unique_lst = []

	# Iterate through the elements in the original list
	for elem in lst:
		# If the element is not already in the unique list, add it
		if elem not in unique_lst:
			unique_lst.append(elem)

	# Return the resulting list
	return unique_lst

def roll_extra_possibility(input_string):
	regex_pattern = r"(.+)\s\((\d+)-in-1D6:\s(.+)\)"
	match = re.match(regex_pattern, input_string)
	if match:
		standard = match.group(1)
		num = int(match.group(2))
		alt = match.group(3)
		roll_result = rnd.randint(1, 6)
		if roll_result <= num:
			return f"{standard} *({alt})*"
		else:
			return standard
	else:
		return input_string

log("Creating generic commands")
@bot.event
async def on_ready():
	log(f"{bot.user} is ready and online!")
	boot_time = int(time.time())

@bot.command(description="Checks how long the bot has been online")
async def uptime(ctx):
	log("/uptime")
	await ctx.respond(f"Online since <t:{boot_time}:D> at <t:{boot_time}:T> (<t:{boot_time}:R>)",ephemeral=True)

@bot.command(description="Measures this bot's latency")
async def ping(ctx):
	log("/ping")
	await ctx.respond(f"Pong! Latency is {bot.latency}")

@bot.command(description="Shuts down the bot. Will not work unless you own the bot.")
async def shutdown(ctx):
	log(f"/shutdown ({ctx.author.id})")
	if ctx.author.id == ownerid:
		await ctx.respond(f"Restarting.")
		await bot.close()
	else:
		await ctx.respond(f"Only <@{ownerid}> may use this command.",ephemeral=True)

@bot.command(description="Links to the Help document for this bot")
async def help(ctx):
	log("/help")
	await ctx.respond("[Full command documentation](https://docs.google.com/document/d/15pm5o5cJuQF_J3l-NMpziPEuxDkcWJVE3TNT7_IerbQ/edit?usp=sharing)",ephemeral=True)

@bot.command(description="Links to the invite page for this bot")
async def invite(ctx):
	log("/invite")
	await ctx.respond("[Invite page](https://discord.com/api/oauth2/authorize?client_id=1096635021395251352&permissions=274877908992&scope=bot%20applications.commands)",ephemeral=True)

@bot.command(description="Links to the support server for this bot")
async def server(ctx):
	log("/server")
	await ctx.respond("https://discord.gg/VeedQmQc7k",ephemeral=True)

@bot.command(description="spin")
async def spin(ctx):
	log("/spin")
	await ctx.respond("[very funny](https://cdn.discordapp.com/attachments/1098474379383423018/1098475477116669952/spin_lq.mp4)",ephemeral=True)

@bot.command(description="testing")
async def debug(ctx, input: discord.Option(str, "data", required=True)):
	log(f"/debug {input}")
	if ctx.author.id == ownerid:
		if len(input) <= 2000:
			await ctx.channel.send(content=input)
			await ctx.respond(f"Done.",ephemeral=True)
		else:
			await ctx.respond(f"Message too long ({len(input)} > 2000).",ephemeral=True)
	else:
		await ctx.respond(f"Only <@{ownerid}> may use this command.",ephemeral=True)

@bot.command(description="Pin (or unpin) a message inside a thread, if you own the thread")
async def threadpin(ctx, id: discord.Option(str, "The ID of the message to pin.", required=True)):
	log(f"/threadpin {id}")
	try:
		channel = ctx.channel
		if type(channel) != discord.Thread:
			await ctx.respond("This command does not work outside of a thread.",ephemeral=True)
		elif channel.owner_id != ctx.author.id:
			await ctx.respond(f"Only <@{channel.owner_id}> may use that command within this thread.",ephemeral=True)
		else:
			id = int(id.strip())
			msg = await channel.fetch_message(id)
			if not msg.pinned:
				await msg.pin(reason=f"/threadpin performed by {ctx.author.name}#{ctx.author.discriminator}")
				await ctx.respond(f"📌 Pinned a message: {msg.jump_url}")
			else:
				await msg.unpin(reason=f"/threadpin performed by {ctx.author.name}#{ctx.author.discriminator}")
				await ctx.respond(f"❌ Unpinned a message: {msg.jump_url}")
	except discord.Forbidden as e:
		log(f"Caught: {e}")
		await ctx.respond(f"There was an error processing this command:\n```{e}```\nThis command does not function properly by default. This bot must have **manage messages** permission.")
	except (discord.NotFound,ValueError) as e:
		log(f"Caught: {e}")
		await ctx.respond(f"There was an error processing this command:\n```{e}```\nYou must provide a valid message ID. Check [this article](<https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID->) for more details.")
	except Exception as e:
		log(f"Caught: {e}")
		await ctx.respond(f"There was an error processing this command:\n```{e}```")

log("Creating trait commands")
trait_group = discord.SlashCommandGroup("trait", "Trait Commands")

async def role_autocomp(ctx):
	return trait_names

@trait_group.command(description="Looks up a trait by name or d666 number")
async def lookup(ctx, trait: discord.Option(str,"The trait to search for",autocomplete=discord.utils.basic_autocomplete(role_autocomp))):
	log(f"/trait lookup {trait}")
	message = search_for_trait(trait)
	hidden = message in ["No trait exists with the given number. Trait numbers must be possible d666 roll outputs.","Could not find a trait with an approximately similar name."]
	
	await ctx.respond(message,ephemeral=hidden)

@trait_group.command(description="Produces a random trait")
async def random(ctx):
	log("/trait random")
	result = rnd.choice(trait_data)
	if (rnd.randint(1,10000) == 1):
		result = secret_trait
	message = trait_message_format(result)
	await ctx.respond(message)

bot.add_application_command(trait_group)

log("Creating role commands")
role_group = discord.SlashCommandGroup("role", "Role Commands")

async def role_autocomp(ctx):
	return role_names

@role_group.command(description="Looks up a role by name or d66 number")
async def lookup(ctx, role: discord.Option(str,"The role to search for",autocomplete=discord.utils.basic_autocomplete(role_autocomp))):
	log(f"/role lookup {role}")
	message = search_for_role(role)
	hidden = message in ["No role exists with the given number. Role numbers must be possible d66 roll outputs.","Could not find a role with an approximately similar name."]
	await ctx.respond(message,ephemeral=hidden)

@role_group.command(description="Produces a random role")
async def random(ctx):
	log("/role random")
	result = rnd.choice(role_data)
	message = role_message_format(result)
	await ctx.respond(message)

bot.add_application_command(role_group)

log("Creating player commands")
player_group = discord.SlashCommandGroup("player", "Player Commands")

def trait_sort_key(trait):
	return trait["Name"]

log("Loading Ripley's codenames")
file = open('ripley_codenames.json')
merc_codenames = json.load(file)
file.close()

@player_group.command(description="Produces a random character sheet")
async def character(ctx, traitcount: discord.Option(discord.SlashCommandOptionType.integer, "The number of traits this character should have. Defaults to 2.", required=False, default=2)):
	log(f"/player character {traitcount}")
	
	message = f"# {rnd.choice(merc_codenames)}"
	if traitcount < 1:
		await ctx.respond("Generated characters must have at least 1 trait.",ephemeral=True)
		return
	if traitcount > 40:
		await ctx.respond("Cannot generate a character with that many traits.",ephemeral=True)
		return
	message += "\nROLE: "
	
	traits = rnd.sample(trait_data, traitcount)
	role = rnd.choice(role_data)
	
	for i in range(len(traits)):
		if (rnd.randint(1,10000) == 1):
			traits[i] = secret_trait
			break
	
	traits.sort(key=trait_sort_key)
	
	extra_thing = rnd.randint(1,3)
	
	message += role_message_format(role) + "\n\n"
	
	stats = {
		"MAX": 6,
		"WAR": 0,
		"FORCEFUL": 0,
		"TACTICAL": 0,
		"CREATIVE": 0,
		"REFLEXIVE": 0
	}
	
	if extra_thing == 1:
		stats["MAX"] += d6()
	elif extra_thing == 2:
		stats["WAR"] += d6()
	
	for trait in traits:
		bonus = trait["Stat"].split(" ")
		num = 0
		if bonus[1] in stats:
			if bonus[0] == "+1D6":
				num = d6()
			else:	
				num = 0
				numerical = bonus[0]
				if numerical[0] in ('+', '-'):
					num = int(numerical[1:])
					if numerical[0] == '-':
						num = -num
				else:
					num = int(numerical)
			
			stats[bonus[1]] += num
	
	message += f"MAX HP: {stats['MAX']}\n"
	message += f"WAR DICE: {stats['WAR']}\n\n"
	message += f"FORCEFUL: {stats['FORCEFUL']}\n"
	message += f"TACTICAL: {stats['TACTICAL']}\n"
	message += f"CREATIVE: {stats['CREATIVE']}\n"
	message += f"REFLEXIVE: {stats['REFLEXIVE']}\n\n"
	
	message += "TRAITS:\n"
	altmessage = message
	for trait in traits:
		message += f"- **{trait['Name']}** ({trait['Number']}): {trait['Effect']} ({trait['Stat']})\n"
		altmessage += f"- **{trait['Name']}** ({trait['Number']}, {trait['Stat']})\n"
	
	altmessage += "\nITEMS:"
	message += "\nITEMS:"
	for trait in traits:
		altmessage += f"\n- {trait['Item']}"
		message += f"\n- {trait['Item']}"
	if extra_thing == 3:
		standard_issue_items = ["Balaclava (hides identity)", "Flashlight (can be used as a weapon attachment)", "Knife (1D6 DAMAGE)", "MRE field rations (+1D6 HP, one use)", "Pistol (1D6 DAMAGE)", "Riot shield (1 ARMOR, equip as weapon)"]
		altmessage += f"\n- {rnd.choice(standard_issue_items)}"
		message += f"\n- {rnd.choice(standard_issue_items)}"
	if len(message) > 2000:
		message = message.replace("FORCEFUL", "FRC")
		message = message.replace("CREATIVE", "CRE")
		message = message.replace("REFLEXIVE", "RFX")
		message = message.replace("TACTICAL", "TAC")
		message = message.replace("DAMAGE", "DMG")
		if len(message) > 2000:
			message = altmessage
	if len(message) > 2000:
		message = message.replace("FORCEFUL", "FRC")
		message = message.replace("CREATIVE", "CRE")
		message = message.replace("REFLEXIVE", "RFX")
		message = message.replace("TACTICAL", "TAC")
		message = message.replace("DAMAGE", "DMG")
		if len(message) > 2000:
			await ctx.respond("The generated character does not fit in the 2,000 character limit for messages. Try lowering the amount of traits.",ephemeral=True)
			return
	await ctx.respond(message)

@player_group.command(description="Rolls against the Emergency Insertion table")
async def emergencyinsertion(ctx):
	log("/player emergencyinsertion")
	results = [d6(), d6()]
	sum = results[0] + results[1]
	
	message = f"{num_to_die[results[0]]} + {num_to_die[results[1]]} = **{sum}**: "
	
	if sum <= 6:
		message += "Deployment goes wrong somehow."
	elif sum <= 9:
		message += "Deploy normally."
	else:
		message += "Deploy with an extra standard issue item"
		if results == [6,6]:
			message += ", **and +3 to your first roll.**"
		else:
			message += "."
	await ctx.respond(message)

@player_group.command(description="Rolls a skill check")
async def roll(ctx, 
	modifier: discord.Option(discord.SlashCommandOptionType.integer, "The skill modifier for the roll", required=False, default=0),
	superior_dice: discord.Option(bool, "Roll 3d6 and take the best two.", required=False, default=False),
	inferior_dice: discord.Option(bool, "Roll 3d6 and take the worst two.", required=False, default=False)
	):
	log(f"/player roll {modifier}{' superior_dice' if superior_dice else ''}{' inferior_dice' if inferior_dice else ''}")
	results = [d6(), d6()]
	if superior_dice ^ inferior_dice:
		results.append(d6())
	
	dice_string = ""
	for d in results:
		dice_string += " " + num_to_die[d]
	dice_string = dice_string.strip()
	
	sorted_results = sorted(results)
	if superior_dice and not inferior_dice:
		results = sorted_results[-2:]
	elif inferior_dice and not superior_dice:
		results = sorted_results[:2]
	
	total = sum(results) + modifier
	
	message = ""
	
	if modifier != 0:
		message = f"({dice_string}) + {modifier} = **{total}**: "
	else:
		message = f"{dice_string} = **{total}**: "
	
	if results == [6,6]:
		message += "Your roll is an **ultra success!** You do exactly what you wanted to do, with some spectacular added bonus."
	elif total <= 6:
		message += "Your roll is a **failure.** You don’t do what you wanted to do, and things go wrong somehow."
	elif total <= 9:
		message += "Your roll is a **partial success.** You do what you wanted to, but with a cost, compromise, or complication."
	else:
		message += "Your roll is a **success.** You do exactly what you wanted to do, without any additional headaches."
	await ctx.respond(message)

@player_group.command(description="Rolls dice using common dice syntax")
async def dice(ctx, syntax: discord.Option(str,"The dice syntax")):
	log(f"/player dice {syntax}")
	timeout = 2
	output = ()
	try:
		output = func_timeout(timeout, rolldice.roll_dice, args=[syntax])
	except rolldice.rolldice.DiceGroupException as e:
		log(f"Caught: {e}")
		await ctx.respond(f"{e}\nSee [py-rolldice](https://github.com/mundungus443/py-rolldice#dice-syntax) for an explanation of dice syntax.",ephemeral=True)
		return
	except FunctionTimedOut as e:
		log(f"Caught: {e}")
		await ctx.respond(f"It took too long to roll your dice (>{timeout}s). Try rolling less dice.",ephemeral=True)
		return
	except (ValueError, rolldice.rolldice.DiceOperatorException) as e:
		log(f"Caught: {e}")
		await ctx.respond(f"Could not properly parse your dice result. This usually means the result is much too large. Try rolling dice that will result in a smaller range of values.",ephemeral=True)
		return
	message = f"**Total: {output[0]}**\n`{output[1]}`"
	limit = 300
	if len(message) > limit:
		message = message[:limit-5]+"...]`"
	if not ('d' in syntax or 'D' in syntax):
		message += f"\n\nIt seems your input didn't actually roll any dice. Did you mean `1d{syntax}` or `{syntax}d6`?\nSee [py-rolldice](<https://github.com/mundungus443/py-rolldice#dice-syntax>) for an explanation of dice syntax."
	await ctx.respond(message)

bot.add_application_command(player_group)

log("Creating matrix commands")
matrix_group = discord.SlashCommandGroup("matrix", "Intelligence Matrix Rollers")

intelligence = {}

file = open('matrices/mission_generator.json')
intelligence["mission"] = json.load(file)
file.close()

@matrix_group.command(description="Provides a random Mission Dossier")
async def mission(ctx):
	log("/matrix mission")
	results = roll_all_matrices(intelligence["mission"])
	instigator = decap_first(results[0])
	activity = decap_first(results[1])
	effect = decap_first(results[2])
	twist = decap_first(results[3])
	reward = results[4]
	message = f"The dossier says that **{instigator}** is trying to **{activity}**, which will **{effect}**. However, **{twist}**.\n- Reward: **{reward}**"
	await ctx.respond(message)

file = open('matrices/mission_prompts.json')
intelligence["prompt"] = json.load(file)
file.close()

@matrix_group.command(description="Provides a random Mission Prompt")
async def prompt(ctx):
	log("/matrix prompt")
	result = roll_intelligence_matrix(intelligence["prompt"][0])
	await ctx.respond(result)

file = open('matrices/misc.json')
intelligence["misc"] = json.load(file)
file.close()

@matrix_group.command(description="Incants a Magical Word")
async def syllables(ctx):
	log("/matrix syllables")
	result = ""
	count = d6()
	for i in range(count):
		result += roll_intelligence_matrix(intelligence["misc"][0])
	await ctx.respond(result)

@matrix_group.command(description="Gives a random Operation Codename")
async def codename(ctx):
	log("/matrix codename")
	result = roll_intelligence_matrix(intelligence["misc"][1])
	await ctx.respond(result)

@matrix_group.command(description="Provokes a random Combat Behavior")
async def tactics(ctx):
	log("/matrix tactics")
	result = roll_intelligence_matrix(intelligence["misc"][2])
	await ctx.respond(result)

@matrix_group.command(description="Strikes a random Hit Location")
async def hit(ctx):
	log("/matrix hit")
	result = [roll_intelligence_matrix(intelligence["misc"][3])]
	while "Compound injury (roll two hit locations)" in result:
		result.append(roll_intelligence_matrix(intelligence["misc"][3]))
		result.append(roll_intelligence_matrix(intelligence["misc"][3]))
		result.remove("Compound injury (roll two hit locations)")
	result = "You've been hit in the **" + "** __*and*__ **".join(result) + "**!"
	await ctx.respond(result)

@matrix_group.command(description="Provokes a random Faction Action")
async def factionaction(ctx):
	log("/matrix factionaction")
	result = [roll_intelligence_matrix(intelligence["misc"][4])]
	while "Fake-out zig-zag (roll two actions)" in result:
		result.append(roll_intelligence_matrix(intelligence["misc"][4]))
		result.append(roll_intelligence_matrix(intelligence["misc"][4]))
		result.remove("Compound injury (roll two hit locations)")
	result = " __*and*__ ".join(result)
	result = f"A faction (any `/matrix faction`) tasks you with the following: **{result}**"
	await ctx.respond(result)

@matrix_group.command(description="Discloses a random Faction Mission")
async def factionmission(ctx):
	log("/matrix factionmission")
	result = [roll_intelligence_matrix(intelligence["misc"][5])]
	while "Double mission (roll two objectives)" in result:
		result.append(roll_intelligence_matrix(intelligence["misc"][5]))
		result.append(roll_intelligence_matrix(intelligence["misc"][5]))
		result.remove("Double mission (roll two objectives)")
	result = " __*and*__ ".join(result)
	message = f"A faction tasks you with this objective: **{result}**"
	await ctx.respond(message)

@matrix_group.command(description="Assigns a random CHOKE Score")
async def choke(ctx):
	log("/matrix choke")
	result = roll_intelligence_matrix(intelligence["misc"][10])
	await ctx.respond(result)

async def part_success_autocomplete(ctx: discord.AutocompleteContext):
	return ["COMBAT","GENERAL","MENTAL","MOVEMENT","SOCIAL","WEIRD"]

@matrix_group.command(description="Causes random consequences for a Partial Success")
async def partial(ctx, type: discord.Option(str,"The type of consequence that should be inflicted",autocomplete=discord.utils.basic_autocomplete(part_success_autocomplete),required=False,default="")):
	log(f"/matrix partial {type}")
	hidden = False
	type = type.upper()
	message = ""
	if type == "":
		message = roll_intelligence_matrix(intelligence["misc"][11])
	elif type in ["COMBAT","GENERAL","MENTAL","MOVEMENT","SOCIAL","WEIRD"]:
		all = intelligence["misc"][11]["Values"].values()
		outcomes = []
		for item in all:
			if item.startswith(type):
				split_point = len(type) + 1
				outcomes.append(item[split_point:])
		message = rnd.choice(outcomes)
	else:
		hidden = True
		message = "Valid partial success types are COMBAT, GENERAL, MOVEMENT, SOCIAL, and WEIRD."
	await ctx.respond(message,ephemeral=hidden)

@matrix_group.command(description="Spawns a Random Encounter")
async def encounter(ctx):
	log("/matrix encounter")
	result = roll_intelligence_matrix(intelligence["misc"][12])
	await ctx.respond(result)

@matrix_group.command(description="Provokes a random Downtime Event")
async def downtime(ctx):
	log("/matrix downtime")
	result = roll_intelligence_matrix(intelligence["misc"][13])
	await ctx.respond(result)

file = open('matrices/cassettes.json')
intelligence["cassettes"] = json.load(file)
file.close()

file = open('matrices/cassette_links.json')
intelligence["cassette_links"] = json.load(file)
file.close()

@matrix_group.command(description="Plays a random Cassette Tape")
async def cassette(ctx):
	log("/matrix cassette")
	audio = rnd.choice(intelligence["cassettes"])
	if audio == "[Combination tape, roll 1D6 tapes]":
		tapes = ["[Combination tape, roll 1D6 tapes]"]
		while "[Combination tape, roll 1D6 tapes]" in tapes:
			tapes = rnd.sample(intelligence["cassettes"], rnd.randint(2,6))
		for i in range(len(tapes)):
			if tapes[i] in intelligence["cassette_links"]:
				tapes[i] = f"[{tapes[i]}](<{intelligence['cassette_links'][tapes[i]]}>)"
		audio = "Combination tape:\n- " + "\n- ".join(tapes)
	elif audio in intelligence["cassette_links"]:
		audio = f"[{audio}](<{intelligence['cassette_links'][audio]}>)"
	await ctx.respond(audio)

gear_group = matrix_group.create_subgroup("gear", "Gear Intelligence Matrices")

file = open('matrices/gear/items.json')
intelligence["gear_items"] = json.load(file)
file.close()

file = open('matrices/gear/weapons_and_armor.json')
intelligence["gear_weapons_and_armor"] = json.load(file)
file.close()

file = open('matrices/gear/vehicles.json')
intelligence["gear_vehicles"] = json.load(file)
file.close()

file = open('matrices/gear/base_upgrades.json')
intelligence["gear_bupgrades"] = json.load(file)
file.close()

bupgrade_names = []
for bupgrade in intelligence["gear_bupgrades"]:
	bupgrade_names.append(bupgrade["Name"])

async def bupgrade_autocomp(ctx):
	return bupgrade_names

@gear_group.command(description="Applies a random Base Upgrade")
async def baseupgrade(ctx, lookup: discord.Option(str,"Including this argument searches for a specific Base Upgrade instead",autocomplete=discord.utils.basic_autocomplete(bupgrade_autocomp),required=False,default="")):
	log("/matrix gear baseupgrade")
	message = ""
	if len(lookup) < 1:
		result = rnd.choice(intelligence["gear_bupgrades"])
		message = f"**{result['Name']}:** {result['Effect']}"
	else:
		best_match = difflib.get_close_matches(lookup.upper(), bupgrade_names, n=1, cutoff=0.0)
		if len(best_match) > 0:
			goodbup = {}
			for bup in intelligence["gear_bupgrades"]:
				if best_match[0] == bup["Name"]:
					goodbup = bup
					break
			message = f"**{goodbup['Name']}:** {goodbup['Effect']}"
	await ctx.respond(message)

@gear_group.command(description="Divulges the contents of a random Crate")
async def crate(ctx):
	log("/matrix gear crate")
	result = roll_intelligence_matrix(intelligence["gear_items"][1])
	message = f"You crack open a crate, revealing **{result}** inside."
	await ctx.respond(message)

@gear_group.command(description="Grants a random Common Item")
async def item(ctx, count: discord.Option(discord.SlashCommandOptionType.integer, "The number of items to produce (allows duplicates)", required=False, default=1)):
	log(f"/matrix gear item {count}")
	max = 50
	if count < 1:
		await ctx.respond("You must generate a minimum of 1 item.",ephemeral=True)
		return
	elif count > max:
		await ctx.respond(f"You may only generate a maximum of {max} items.",ephemeral=True)
		return
	results = {}
	for i in range(count):
		item = roll_intelligence_matrix(intelligence["gear_items"][0])
		if item not in results:
			results[item] = 1
		else:
			results[item] = results[item] + 1
	joinlist = []
	for key in sorted(list(results.keys())):
		if results[key] > 1:
			joinlist.append(f"{key} **(x{results[key]})**")
		else:
			joinlist.append(key)
	message = "\n".join(joinlist)
	await ctx.respond(message)

@gear_group.command(description="Grants a random piece of Armor")
async def armor(ctx, count: discord.Option(discord.SlashCommandOptionType.integer, "The number of armor pieces to produce (allows duplicates)", required=False, default=1)):
	log("/matrix gear armor")
	max = 50
	if count < 1:
		await ctx.respond("You must generate a minimum of 1 armor piece.",ephemeral=True)
		return
	elif count > max:
		await ctx.respond(f"You may only generate a maximum of {max} armor pieces.",ephemeral=True)
		return
	results = {}
	for i in range(count):
		item = roll_intelligence_matrix(intelligence["gear_weapons_and_armor"][0])
		if item not in results:
			results[item] = 1
		else:
			results[item] = results[item] + 1
	joinlist = []
	for key in sorted(list(results.keys())):
		if results[key] > 1:
			joinlist.append(f"{key} **(x{results[key]})**")
		else:
			joinlist.append(key)
	message = "\n".join(joinlist)
	await ctx.respond(message)

@gear_group.command(description="Grants a random Weapon")
async def weapon(ctx, count: discord.Option(discord.SlashCommandOptionType.integer, "The number of weapons to produce (allows duplicates)", required=False, default=1)):
	log(f"/matrix gear weapon {count}")
	max = 50
	if count < 1:
		await ctx.respond("You must generate a minimum of 1 weapon.",ephemeral=True)
		return
	elif count > max:
		await ctx.respond(f"You may only generate a maximum of {max} weapons.",ephemeral=True)
		return
	results = {}
	for i in range(count):
		item = roll_intelligence_matrix(intelligence["gear_weapons_and_armor"][1])
		if item not in results:
			results[item] = 1
		else:
			results[item] = results[item] + 1
	joinlist = []
	for key in sorted(list(results.keys())):
		if results[key] > 1:
			joinlist.append(f"{key} **(x{results[key]})**")
		else:
			joinlist.append(key)
	message = "\n".join(joinlist)
	await ctx.respond(message)

wep_tag_names = []
for tag in intelligence["gear_weapons_and_armor"][2]["Values"].values():
	wep_tag_names.append(tag['Name'])

async def tag_lookup_autocomp(ctx):
	return wep_tag_names

@gear_group.command(description="Applies a random Weapon Tag")
async def tag(ctx, lookup: discord.Option(str,"Including this argument searches for a specific tag instead",autocomplete=discord.utils.basic_autocomplete(tag_lookup_autocomp),required=False,default="")):
	log("/matrix gear tag")
	tags = intelligence["gear_weapons_and_armor"][2]["Values"]
	message = ""
	hidden = False
	if lookup == "":
		result = roll_intelligence_matrix(intelligence["gear_weapons_and_armor"][2])
		message = f"**{result['Name']}**: {result['Effect']}"
	else:
		if re.match("^\d+$", lookup):
			if lookup in tags:
				result = tags[lookup]
				message = f"**{result['Name']}**: {result['Effect']}"
			else:
				message = "No tag exists with the given number. Tag numbers must be possible d66 roll outputs."
				hidden = True
		else:
			best_match = difflib.get_close_matches(lookup.upper(), wep_tag_names, n=1, cutoff=0.0)
			
			if len(best_match) > 0:
				for tag in tags.values():
					if tag["Name"] == best_match[0]:
						result = tag
						message = f"**{result['Name']}**: {result['Effect']}"
						break
			else:
				message = "Could not find a tag with an approximately similar name."
				hidden = True
	await ctx.respond(message,ephemeral=hidden)

@gear_group.command(description="Grants a random Vehicle")
async def vehicle(ctx, count: discord.Option(discord.SlashCommandOptionType.integer, "The number of vehicles to produce (allows duplicates)", required=False, default=1)):
	log(f"/matrix gear vehicle {count}")
	max = 50
	if count < 1:
		await ctx.respond("You must generate a minimum of 1 vehicle.",ephemeral=True)
		return
	elif count > max:
		await ctx.respond(f"You may only generate a maximum of {max} vehicles.",ephemeral=True)
		return
	results = {}
	for i in range(count):
		item = roll_intelligence_matrix(intelligence["gear_vehicles"][0])
		if item not in results:
			results[item] = 1
		else:
			results[item] = results[item] + 1
	joinlist = []
	for key in sorted(list(results.keys())):
		if results[key] > 1:
			joinlist.append(f"{key} **(x{results[key]})**")
		else:
			joinlist.append(key)
	message = "\n".join(joinlist)
	await ctx.respond(message)

@gear_group.command(description="Grants a random Vehicle Weapon")
async def vehicleweapon(ctx, count: discord.Option(discord.SlashCommandOptionType.integer, "The number of vehicle weapons to produce (allows duplicates)", required=False, default=1)):
	log(f"/matrix gear vehicleweapon {count}")
	max = 50
	if count < 1:
		await ctx.respond("You must generate a minimum of 1 vehicle weapon.",ephemeral=True)
		return
	elif count > max:
		await ctx.respond(f"You may only generate a maximum of {max} vehicle weapons.",ephemeral=True)
		return
	results = {}
	for i in range(count):
		item = roll_intelligence_matrix(intelligence["gear_vehicles"][1])
		if item not in results:
			results[item] = 1
		else:
			results[item] = results[item] + 1
	joinlist = []
	for key in sorted(list(results.keys())):
		if results[key] > 1:
			joinlist.append(f"{key} **(x{results[key]})**")
		else:
			joinlist.append(key)
	message = "\n".join(joinlist)
	await ctx.respond(message)

@gear_group.command(description="Applies a random Weapon Skin")
async def skin(ctx, count: discord.Option(discord.SlashCommandOptionType.integer, "The number of weapon skins to produce (allows duplicates)", required=False, default=1)):
	log(f"/matrix gear skin {count}")
	max = 50
	if count < 1:
		await ctx.respond("You must generate a minimum of 1 weapon skin.",ephemeral=True)
		return
	elif count > max:
		await ctx.respond(f"You may only generate a maximum of {max} weapon skins.",ephemeral=True)
		return
	results = {}
	for i in range(count):
		item = roll_intelligence_matrix(intelligence["gear_weapons_and_armor"][3])
		if item not in results:
			results[item] = 1
		else:
			results[item] = results[item] + 1
	joinlist = []
	for key in sorted(list(results.keys())):
		if results[key] > 1:
			joinlist.append(f"{key} **(x{results[key]})**")
		else:
			joinlist.append(key)
	message = "\n".join(joinlist)
	await ctx.respond(message)

@gear_group.command(description="Generates a fully unique Weapon")
async def weaponsmith(ctx):
	log("/matrix gear weaponsmith")
	model = roll_intelligence_matrix(intelligence["gear_weapons_and_armor"][1])
	tag = roll_intelligence_matrix(intelligence["gear_weapons_and_armor"][2])
	tag = f"**{tag['Name']}**: {tag['Effect']}"
	skin = roll_intelligence_matrix(intelligence["gear_weapons_and_armor"][3])
	message = f"**{model}** (adorned with **{skin}**)\n- {tag}"
	await ctx.respond(message)

@gear_group.command(description="Generates a fully unique Vehicle")
async def hangar(ctx):
	log("/matrix gear weaponsmith")
	model = roll_intelligence_matrix(intelligence["gear_vehicles"][0])
	weapon = roll_intelligence_matrix(intelligence["gear_vehicles"][1])
	skin = roll_intelligence_matrix(intelligence["gear_weapons_and_armor"][3])
	message = f"**{model}**\n- Equipped with **{weapon}**\n- Adorned with **{skin}**"
	await ctx.respond(message)

cyclops_group = matrix_group.create_subgroup("cyclops", "CYCLOPS Intelligence Matrices")

file = open('matrices/cyclops/gadgets.json')
intelligence["cyclops_gadgets"] = json.load(file)
file.close()

file = open('matrices/cyclops/rumors.json')
intelligence["cyclops_rumors"] = json.load(file)
file.close()

@cyclops_group.command(description="Grants a random CYCLOPS Gadget")
async def gadget(ctx, 
	count: discord.Option(discord.SlashCommandOptionType.integer, "The number of CYCLOPS Gadgets to produce", required=False, default=1),
	duplicates: discord.Option(bool, "Mark FALSE to prevent duplicate items being rolled if count > 1", required=False, default=True)
	):
	log(f"/matrix cyclops gadget {count}{' no_duplicates' if not duplicates else ''}")
	message = ""
	limit = 250
	if count > limit:
		await ctx.respond(f"Please do not produce more than {limit} gadgets.",ephemeral=True)
		return
	elif count <= 1:
		result = roll_intelligence_matrix(intelligence["cyclops_gadgets"][0])
		message = f"**{result['Name']}**: {result['Effect']}"
	else:
		if duplicates:
			results = {}
			for i in range(count):
				g = roll_intelligence_matrix(intelligence["cyclops_gadgets"][0])
				name = g["Name"]
				if name in results:
					results[name] = results[name] + 1
				else:
					results[name] = 1
			for key in results:
				if results[key] > 1:
					message += f"{key} **(x{results[key]})**\n"
				else:
					message += f"{key}\n"
		else:
			gs = list(intelligence["cyclops_gadgets"][0]["Values"].values())
			outs = rnd.sample(gs, min([len(gs),count]))
			for item in outs:
				message += f"{item['Name']}\n"
	await ctx.respond(message)

@cyclops_group.command(description="Divulges where CYCLOPS High Command is (allegedly) located")
async def location(ctx):
	log("/matrix cyclops location")
	result = roll_intelligence_matrix(intelligence["cyclops_rumors"][0])
	message = f"Rumored location of CYCLOPS High Command: **{result}**"
	await ctx.respond(message)

@cyclops_group.command(description="Divulges the (alleged) origin of CYCLOPS")
async def origin(ctx):
	log("/matrix cyclops origin")
	result = roll_intelligence_matrix(intelligence["cyclops_rumors"][1])
	message = f"Rumored origin of CYCLOPS: **{result}**"
	await ctx.respond(message)

world_group = matrix_group.create_subgroup("world", "World Intelligence Matrices")

file = open('matrices/world/hazards.json')
intelligence["world_hazards"] = json.load(file)
file.close()

@world_group.command(description="Spawns a random Hazard")
async def hazard(ctx):
	log("/matrix world hazard")
	result = roll_intelligence_matrix(intelligence["world_hazards"][0])
	message = f"Tread carefully; the area ahead contains **{result.lower()}**."
	await ctx.respond(message)

@world_group.command(description="Reveals a random Trap")
async def trap(ctx):
	log("/matrix world trap")
	result = roll_intelligence_matrix(intelligence["world_hazards"][1])
	message = f"You've sprung a trap! You suffer the effects of **{result.lower()}**."
	await ctx.respond(message)

@world_group.command(description="Starts in a random Year")
async def year(ctx):
	log("/matrix world year")
	start = int(roll_intelligence_matrix(intelligence["misc"][6]))
	modifier = int(roll_intelligence_matrix(intelligence["misc"][7]))
	year = start + modifier
	await ctx.respond(f"_The year is **{year}**..._")

@world_group.command(description="Randomly modifies the local Temperature and Precipitation")
async def weather(ctx):
	log("/matrix world weather")
	temp = roll_intelligence_matrix(intelligence["misc"][8])
	precip = roll_intelligence_matrix(intelligence["misc"][9])
	result = f"**Temperature:** {temp}\n**Precipitation:** {precip}"
	await ctx.respond(result)

chars_group = matrix_group.create_subgroup("character", "Character Intelligence Matrices")

def format_premade(structure):
	output = "**"
	output += structure["Head"].replace(" (", "** (", 1)
	for feat in structure["Features"]:
		output += "\n- " + feat
	for note in structure["Notes"]:
		output += "\n**" + note.replace(":", ":**", 1)
	return output

file = open('matrices/characters/premade_npcs.json')
intelligence["chars_premade"] = json.load(file)
file.close()

premade_npc_names = []
for char in intelligence["chars_premade"]:
	name = char["Head"].strip()
	index = name.find(" (")
	if index != -1:
		name = name[:index]
	premade_npc_names.append(name)

async def npc_lookup_autocomp(ctx):
	return premade_npc_names

@chars_group.command(description="Spawns a random pre-made NPC")
async def premade(ctx, lookup: discord.Option(str,"Including this argument searches for a specific NPC instead",autocomplete=discord.utils.basic_autocomplete(npc_lookup_autocomp),required=False,default="")):
	log(f"/matrix character premade {lookup}")
	message = ""
	if len(lookup) < 1:
		result = rnd.choice(intelligence["chars_premade"])
		message = format_premade(result)
	else:
		best_match = difflib.get_close_matches(lookup.upper(), premade_npc_names, n=1, cutoff=0.0)
		if len(best_match) > 0:
			goodchar = {}
			for char in intelligence["chars_premade"]:
				if best_match[0] in char["Head"]:
					goodchar = char
					break
			message = format_premade(goodchar)
	await ctx.respond(message)

file = open('matrices/characters/celebrities.json')
intelligence["chars_celebs"] = json.load(file)
file.close()

@chars_group.command(description="Spawns a random Celebrity")
async def celebrity(ctx):
	log("/matrix character celebrity")
	result = roll_all_matrices(intelligence["chars_celebs"])
	profession = [result[0]]
	while "Roll twice, ignoring duplicates" in profession:
		profession.remove("Roll twice, ignoring duplicates")
		profession.append(roll_intelligence_matrix(intelligence["chars_celebs"][0]))
		profession.append(roll_intelligence_matrix(intelligence["chars_celebs"][0]))
	profession = remove_duplicates(profession)
	profession = ", ".join(profession)
	name = result[1]
	feature = result[2]
	story = result[3]
	message = f"Name: {name}\nProfession: {profession}\nFeature: {feature}\nStory: {story}"
	await ctx.respond(message)

file = open('matrices/characters/civilians.json')
intelligence["chars_civvies"] = json.load(file)
file.close()

@chars_group.command(description="Spawns a random Civilian")
async def civilian(ctx):
	log("/matrix character civilian")
	result = roll_all_matrices(intelligence["chars_civvies"])
	job = result[0]
	name = result[1]
	feature = result[2]
	story = result[3]
	message = f"Name: {name}\nJob: {job}\nFeature: {feature}\nStory: {story}"
	await ctx.respond(message)

file = open('matrices/characters/politicians.json')
intelligence["chars_politicians"] = json.load(file)
file.close()

@chars_group.command(description="Spawns a random Politician")
async def politician(ctx):
	log("/matrix character politician")
	result = roll_all_matrices(intelligence["chars_politicians"])
	position = result[0]
	vice = result[1]
	name = result[2]
	feature = result[3]
	secret = result[4]
	message = f"Name: {name}\nPosition: {position}\nVice: {vice}\nFeature: {feature}\nSecret: {secret}"
	await ctx.respond(message)

file = open('matrices/characters/scientists.json')
intelligence["chars_scientists"] = json.load(file)
file.close()

@chars_group.command(description="Spawns a random Scientist")
async def scientist(ctx):
	log("/matrix character scientist")
	result = roll_all_matrices(intelligence["chars_scientists"])
	alleg = result[0]
	career = result[1]
	name = result[2]
	feature = result[3]
	discovery = roll_extra_possibility(result[4])
	message = f"Name: {name}\nAllegiance: {alleg}\nCareer: {career}\nFeature: {feature}\nDiscovery: {discovery}"
	await ctx.respond(message)

file = open('matrices/characters/soldiers.json')
intelligence["chars_soldiers"] = json.load(file)
file.close()

@chars_group.command(description="Spawns a random Soldier")
async def soldier(ctx):
	log("/matrix character soldier")
	result = roll_all_matrices(intelligence["chars_soldiers"])
	rank = result[0]
	name = result[1]
	feature = result[2]
	anecdote = result[3]
	message = f"Name: {name}\nRank: {rank}\nFeature: {feature}\nAnecdote: {anecdote}"
	await ctx.respond(message)
	
file = open('matrices/characters/spies.json')
intelligence["chars_spies"] = json.load(file)
file.close()

@chars_group.command(description="Spawns a random Spy")
async def spy(ctx):
	log("/matrix character spy")
	result = roll_all_matrices(intelligence["chars_spies"])
	code = result[0]
	clearance = result[1]
	name = result[2]
	feature = result[3]
	modus = result[4]
	message = f"Name: {name}\nCodename: {code}\nClearance: {clearance}\nFeature: {feature}\nModus: {modus}"
	await ctx.respond(message)

enemy_group = matrix_group.create_subgroup("enemy", "Enemy Intelligence Matrices")

file = open('matrices/characters/premade_enemies.json')
intelligence["chars_enemy_premade"] = json.load(file)
file.close()

premade_enemy_names = []
for char in intelligence["chars_enemy_premade"]:
	name = char["Head"].replace("(BOSS) ", "").strip()
	index = name.find(" (")
	if index != -1:
		name = name[:index]
	premade_enemy_names.append(name)

async def enemy_lookup_autocomp(ctx):
	return premade_enemy_names

@enemy_group.command(description="Spawns a random pre-made Enemy")
async def premade(ctx, lookup: discord.Option(str,"Including this argument searches for a specific Enemy instead",autocomplete=discord.utils.basic_autocomplete(enemy_lookup_autocomp),required=False,default="")):
	log(f"/matrix enemy premade {lookup}")
	message = ""
	if len(lookup) < 1:
		result = rnd.choice(intelligence["chars_enemy_premade"])
		message = format_premade(result)
	else:
		best_match = difflib.get_close_matches(lookup.upper(), premade_enemy_names, n=1, cutoff=0.0)
		if len(best_match) > 0:
			goodchar = {}
			for char in intelligence["chars_enemy_premade"]:
				if best_match[0] in char["Head"]:
					goodchar = char
					break
			message = format_premade(goodchar)
	await ctx.respond(message)

file = open('matrices/characters/animals.json')
intelligence["chars_animals"] = json.load(file)
file.close()

@enemy_group.command(description="Spawns a random Animal")
async def animal(ctx):
	log("/matrix enemy animal")
	result = roll_all_matrices(intelligence["chars_animals"])
	amount = result[0]
	desc = result[1]
	feature = result[2]
	mal = result[3]
	message = f"Description: {desc}\nAmount: {amount}\nFeature: {feature}\nMalady: {mal}"
	await ctx.respond(message)

file = open('matrices/characters/anomalies.json')
intelligence["chars_anomalies"] = json.load(file)
file.close()

@enemy_group.command(description="Spawns a random Anomaly")
async def anomaly(ctx):
	log("/matrix enemy anomaly")
	result = roll_all_matrices(intelligence["chars_anomalies"])
	signature = result[0]
	desc = result[1]
	feature = result[2]
	sighting = result[3]
	message = f"Description: {desc}\nSignature: {signature}\nFeature: {feature}\nSighting: {sighting}"
	await ctx.respond(message)

file = open('matrices/characters/experiments.json')
intelligence["chars_experiments"] = json.load(file)
file.close()

@enemy_group.command(description="Performs a random Experiment")
async def experiment(ctx):
	log("/matrix enemy experiment")
	result = roll_all_matrices(intelligence["chars_experiments"])
	creation = result[0]
	desc = result[1]
	feature = result[2]
	mistake = result[3]
	if creation == "Uncontrolled\u2014Roll 1D6 extra features":
		feature = [feature]
		more = d6()
		for i in range(more):
			feature.append(roll_intelligence_matrix(intelligence["chars_experiments"][2]))
		feature = ", ".join(feature)
	elif creation == "Accidental\u2014Roll 1D6 extra mistakes":
		mistake = [mistake]
		more = d6()
		for i in range(more):
			mistake.append(roll_intelligence_matrix(intelligence["chars_experiments"][3]))
		mistake = ", ".join(mistake)
	message = f"Description: {desc}\nCreation: {creation}\nFeature: {feature}\nMistake: {mistake}"
	await ctx.respond(message)

file = open('matrices/characters/monsters.json')
intelligence["chars_monsters"] = json.load(file)
file.close()

@enemy_group.command(description="Spawns a random Monster")
async def monster(ctx):
	log("/matrix enemy monster")
	result = roll_all_matrices(intelligence["chars_monsters"])
	amount = result[0]
	desc = result[1]
	feature = result[2]
	horror = result[3]
	if amount == "Dire (3-6 ARMOR, 6D6-10D6 HP, roll another horror)":
		horror += " __*and*__ " + roll_intelligence_matrix(intelligence["chars_monsters"][3])
	message = f"Description: {desc}\nAmount: {amount}\nFeature: {feature}\nHorror: {horror}"
	await ctx.respond(message)

file = open('matrices/characters/robots.json')
intelligence["chars_robots"] = json.load(file)
file.close()

@enemy_group.command(description="Spawns a random Robot")
async def robot(ctx):
	log("/matrix enemy robot")
	result = roll_all_matrices(intelligence["chars_robots"])
	budget = result[0]
	desc = result[1]
	feature = result[2]
	prog = result[3]
	
	if budget == "Federal\u2014roll again for conflicting programming":
		prog_conflict = roll_intelligence_matrix(intelligence["chars_robots"][3])
		while prog_conflict == prog:
			prog_conflict = roll_intelligence_matrix(intelligence["chars_robots"][3])
		prog = f"{prog} (conflicts with: {prog_conflict})"
	elif budget == "CYCLOPS\u2014add 1D6 additional features":
		possible_features = list(intelligence["chars_robots"][2]["Values"].values())
		feature = rnd.sample(possible_features,1+d6())
		feature = ", ".join(feature)
	elif budget == "Corporate\u2014mash together 1D6 descriptions":
		possible_descs = list(intelligence["chars_robots"][1]["Values"].values())
		desc = rnd.sample(possible_descs,rnd.randint(2,6))
		desc = ", ".join(desc)
	
	message = f"Description: {desc}\nBudget: {budget}\nFeature: {feature}\nProgramming: {prog}"
	await ctx.respond(message)

file = open('matrices/characters/squads.json')
intelligence["chars_squads"] = json.load(file)
file.close()

@enemy_group.command(description="Spawns a random Squad")
async def squad(ctx):
	log("/matrix enemy squad")
	result = roll_all_matrices(intelligence["chars_squads"])
	rep = result[0]
	command = result[1]
	name = result[2]
	feature = result[3]
	if d6() <= 3:
		feature = f"{feature} __*and*__ {roll_intelligence_matrix(intelligence['chars_squads'][3])}"
	theme = result[4]
	message = f"Name: {name}\nReputation: {rep}\nFeature: {feature}\nTheme: {theme}"
	await ctx.respond(message)

fact_group = matrix_group.create_subgroup("faction", "Faction Intelligence Matrices")

file = open('matrices/factions/aliens.json')
intelligence["facs_aliens"] = json.load(file)
file.close()

@fact_group.command(description="Establishes a random Alien faction")
async def aliens(ctx):
	log("/matrix faction aliens")
	result = roll_all_matrices(intelligence["facs_aliens"])
	origin = result[0]
	mission = result[1]
	desc = result[2]
	feature = result[3]
	truth = roll_extra_possibility(result[4])
	message = f"Description: {desc}\nFeature: {feature}\nMission: {mission}\nOrigin: {origin}\nTruth: {truth}"
	await ctx.respond(message)

file = open('matrices/factions/agencies.json')
intelligence["facs_agencies"] = json.load(file)
file.close()

@fact_group.command(description="Establishes a random Agency")
async def agency(ctx):
	log("/matrix faction agency")
	result = roll_all_matrices(intelligence["facs_agencies"])
	parent = result[0]
	name = result[1]
	feature = result[2]
	function = result[3]
	message = f"Name: {name}\nFeature: {feature}\nParent: {parent}\nFunction: {function}"
	await ctx.respond(message)

file = open('matrices/factions/corporations.json')
intelligence["facs_corporations"] = json.load(file)
file.close()

@fact_group.command(description="Establishes a random Corporation")
async def corporation(ctx):
	log("/matrix faction corporation")
	result = roll_all_matrices(intelligence["facs_corporations"])
	sector = result[0]
	if sector == "Megacorp (roll 1D6 sectors)":
		possible_sectors = list(intelligence["facs_corporations"][0]["Values"].values())
		possible_sectors.remove("Megacorp (roll 1D6 sectors)")
		subsectors = rnd.sample(possible_sectors,rnd.randint(2,6))
		sector = f"Megacorp ({', '.join(subsectors)})"
	name = result[1]
	feature = result[2]
	scheme = result[3]
	message = f"Name: {name}\nSector: {sector}\nFeature: {feature}\nScheme: {scheme}"
	await ctx.respond(message)

file = open('matrices/factions/criminals.json')
intelligence["facs_criminals"] = json.load(file)
file.close()

@fact_group.command(description="Establishes a random Criminal organization")
async def criminals(ctx):
	log("/matrix faction criminals")
	result = roll_all_matrices(intelligence["facs_criminals"])
	honor = result[0]
	name = result[1]
	feature = result[2]
	racket = result[3]
	message = f"Name: {name}\nFeature: {feature}\nRacket: {racket}\nHonor: {honor}"
	await ctx.respond(message)

file = open('matrices/factions/cults.json')
intelligence["facs_cults"] = json.load(file)
file.close()

@fact_group.command(description="Establishes a random Cult")
async def cult(ctx):
	log("/matrix faction cult")
	result = roll_all_matrices(intelligence["facs_cults"])
	lead = result[0]
	size = result[1]
	desc = result[2]
	feature = result[3]
	prophecy = result[4]
	message = f"Description: {desc}\nFeature: {feature}\nLeadership: {lead}\nSize: {size}\nProphecy: *\"{prophecy}!\"*"
	await ctx.respond(message)

file = open('matrices/factions/insurgents.json')
intelligence["facs_insurgents"] = json.load(file)
file.close()

@fact_group.command(description="Establishes a random Insurgent group")
async def insurgents(ctx):
	log("/matrix faction insurgents")
	result = roll_all_matrices(intelligence["facs_insurgents"])
	foothold = result[0]
	desc = result[1]
	feature = result[2]
	strategy = result[3]
	if strategy == "Spin a new image of their ideology, reroll description":
		desc2 = roll_intelligence_matrix(intelligence['facs_insurgents'][1])
		while desc2 == desc:
			desc2 = roll_intelligence_matrix(intelligence['facs_insurgents'][1])
		desc = f"{desc} (being spun as {desc2})"
	message = f"Description: {desc}\nFeature: {feature}\nFoothold: {foothold}\nStrategy: {strategy}"
	await ctx.respond(message)

loc_group = matrix_group.create_subgroup("location", "Location Intelligence Matrices")

file = open('matrices/locations/battlefields.json')
intelligence["locs_battlefields"] = json.load(file)
file.close()

@loc_group.command(description="Locates a random Battlefield")
async def battlefield(ctx):
	log("/matrix location battlefield")
	result = roll_all_matrices(intelligence["locs_battlefields"])
	layout = result[0]
	desc = result[1]
	feature = result[2]
	grave = roll_extra_possibility(result[3])
	message = f"Layout: {layout}\nDescription: {desc}\nFeature: {feature}\nGrave: {grave}"
	await ctx.respond(message)

file = open('matrices/locations/cities.json')
intelligence["locs_cities"] = json.load(file)
file.close()

@loc_group.command(description="Locates a random City")
async def city(ctx):
	log("/matrix location city")
	result = roll_all_matrices(intelligence["locs_cities"])
	cyclops = result[0]
	name = result[1]
	feature = result[2]
	headline = result[3]
	message = f"Name: {name}\nFeature: {feature}\nCyclops Surveillance Level: {cyclops}\nHeadline: *{headline}*"
	await ctx.respond(message)

file = open('matrices/locations/nature.json')
intelligence["locs_nature"] = json.load(file)
file.close()

@loc_group.command(description="Locates a random location in Nature")
async def nature(ctx):
	log("/matrix location nature")
	result = roll_all_matrices(intelligence["locs_nature"])
	situation = result[0]
	desc = result[1]
	feature = result[2]
	claim = result[3]
	if situation == "Shaky\u2014roll two claims, situation deteriorating":
		claim += " __*and*__ " + roll_intelligence_matrix(intelligence["locs_nature"][3])
	elif situation in ["Powder keg\u2014roll 1D6 claims, tensions are high","War\u2014roll 1D6 claims, active conflict in the area"]:
		possible_claims = list(intelligence["locs_nature"][3]["Values"].values())
		subclaims = rnd.sample(possible_claims, d6())
		claim = '\n- ' + '\n- '.join(subclaims)
	message = f"Description: {desc}\nFeature: {feature}\nSituation: {situation}\nClaim: {claim}"
	await ctx.respond(message)

file = open('matrices/locations/rooms.json')
intelligence["locs_rooms"] = json.load(file)
file.close()

@loc_group.command(description="Locates a random Room")
async def room(ctx):
	log("/matrix location room")
	result = roll_all_matrices(intelligence["locs_rooms"])
	exits = result[0]
	doors = result[1]
	desc = result[2]
	feature = result[3]
	event = result[4]
	message = f"Description: {desc}\nFeature: {feature}\nDoors: {doors}\nExits: {exits}\nEvent: {event}"
	await ctx.respond(message)

file = open('matrices/locations/structures.json')
intelligence["locs_structures"] = json.load(file)
file.close()

@loc_group.command(description="Locates a random Structure")
async def structure(ctx):
	log("/matrix location structure")
	result = roll_all_matrices(intelligence["locs_structures"])
	owner = result[0]
	security = result[1]
	desc = result[2]
	feature = result[3]
	history = result[4]
	message = f"Description: {desc}\nFeature: {feature}\nOwner: {owner}\nSecurity: {security}\nHistory: {history}"
	await ctx.respond(message)


file = open('matrices/locations/zones.json')
intelligence["locs_zones"] = json.load(file)
file.close()

@loc_group.command(description="Locates a random Zone")
async def zone(ctx):
	log("/matrix location zone")
	result = roll_all_matrices(intelligence["locs_zones"])
	size = result[0]
	integrity = result[1]
	desc = result[2]
	feature = result[3]
	center = result[4]
	message = f"Size: {size}\nDescription: {desc}\nFeature: {feature}\nIntegrity: {integrity}\nCenter: {center}"
	await ctx.respond(message)

lore_group = matrix_group.create_subgroup("lore", "Lore Intelligence Matrices")

file = open('matrices/lore/artifacts.json')
intelligence["lore_artifacts"] = json.load(file)
file.close()

def starts_with_vowel(word):
	vowels = ['a', 'e', 'i', 'o', 'u']
	if word[0].lower() in vowels:
		return "an"
	else:
		return "a"

@lore_group.command(description="Forges a random Artifact")
async def artifact(ctx):
	log("/matrix lore artifact")
	result = roll_all_matrices(intelligence["lore_artifacts"])
	interest = result[0]
	desc = result[1]
	feature = result[2]
	rumor = result[3]
	if rumor == "Conflicting archaeological accounts, reroll feature":
		second_feature = feature
		while feature == second_feature:
			second_feature = roll_intelligence_matrix(intelligence["lore_artifacts"][2])
		feature = f"{feature} *(but some say... {second_feature})*"
	elif rumor == "Hearsay has warped its image, reroll description":
		second_desc = desc
		while desc == second_desc:
			second_desc = roll_intelligence_matrix(intelligence["lore_artifacts"][1])
		a = starts_with_vowel(second_desc)
		desc = f"{desc} *(but lately, people believe it's {a} {second_desc})*"
	elif rumor == "Secret race to claim it, reroll interest":
		second_interest = interest
		while interest == second_interest:
			second_interest = roll_intelligence_matrix(intelligence["lore_artifacts"][0])
		interest = f"{interest} *(but more recently, it's {second_interest})*"
	message = f"Description: {desc}\nFeature: {feature}\nRumor: {rumor}\nInterest: {interest}"
	await ctx.respond(message)

file = open('matrices/lore/coverups.json')
intelligence["lore_coverups"] = json.load(file)
file.close()

@lore_group.command(description="Uncovers a random Coverup")
async def coverup(ctx):
	log("/matrix lore coverup")
	result = roll_all_matrices(intelligence["lore_coverups"])
	suppression = result[0]
	witness = result[1]
	if witness == "1D6 witnesses":
		witness = f"{rnd.randint(2,6)} witnesses"
	desc = result[2]
	feature = result[3]
	hook = result[4]
	message = f"Suppression: {suppression}\nWitness: {witness}\nDescription: {desc}\nFeature: {feature}\nHook: {hook}"
	await ctx.respond(message)

file = open('matrices/lore/diplomacy.json')
intelligence["lore_diplomacy"] = json.load(file)
file.close()

@lore_group.command(description="Establishes a random Diplomacy")
async def diplomacy(ctx):
	log("/matrix lore diplomacy")
	result = roll_all_matrices(intelligence["lore_diplomacy"])
	coverage = result[0]
	desc = result[1]
	feature = result[2]
	drama = result[3]
	message = f"Description: {desc}\nFeature: {feature}\nCoverage: {coverage}\nDrama: {drama}"
	await ctx.respond(message)

file = open('matrices/lore/disasters.json')
intelligence["lore_disasters"] = json.load(file)
file.close()

@lore_group.command(description="Causes a random Disaster")
async def disaster(ctx):
	log("/matrix lore disaster")
	result = roll_all_matrices(intelligence["lore_disasters"])
	scale = result[0]
	response = result[1]
	desc = result[2]
	feature = result[3]
	impact = result[4]
	message = f"Description: {desc}\nFeature: {feature}\nScale: {scale}\nResponse: {response}\nImpact: {impact}"
	await ctx.respond(message)

file = open('matrices/lore/legends.json')
intelligence["lore_legends"] = json.load(file)
file.close()

@lore_group.command(description="Tells a random Legend")
async def legend(ctx):
	log("/matrix lore legend")
	result = roll_all_matrices(intelligence["lore_legends"])
	fate = result[0]
	if fate == "Many threads (roll two fates)":
		possible_fates = list(intelligence["lore_legends"][0]["Values"].values())
		possible_fates.remove("Many threads (roll two fates)")
		fates = rnd.sample(possible_fates, 2)
		fate = f"Many threads ({' and '.join(fates)})"
	desc = result[1]
	feature = result[2]
	achieve = result[3]
	while d6() <= 2:
		possible_achieves = list(intelligence["lore_legends"][3]["Values"].values())
		achieve += f" (or maybe {rnd.choice(possible_achieves)})"
	message = f"Description: {desc}\nFeature: {feature}\nAchievement: {achieve}\nUltimate Fate: {fate}"
	await ctx.respond(message)

file = open('matrices/lore/spells.json')
intelligence["lore_spells"] = json.load(file)
file.close()

@lore_group.command(description="Casts a random Spell")
async def spell(ctx):
	log("/matrix lore spell")
	result = roll_all_matrices(intelligence["lore_spells"])
	level = result[0]
	obscurity = result[1]
	name = result[2]
	if d6() <= 2:
		names = rnd.sample(list(intelligence["lore_spells"][2]["Values"].values()),2)
		names[0] = names[0].rsplit(" ", 1)
		names[1] = names[1].rsplit(" ", 1)
		name = names[0][0] + " " + names[1][1]
	feature = result[3]
	effect = result[4]
	message = f"Name: {name}\nEffect: {effect}\nFeature: {feature}\nLevel: {level}\nObscurity: {obscurity}"
	await ctx.respond(message)

bot.add_application_command(matrix_group)

atrx_group = discord.SlashCommandGroup("ataraxia", "RATIONS #1: ATARAXIA Commands")

file = open('rations/ataraxia.json')
intelligence["ataraxia"] = json.load(file)
file.close()

@atrx_group.command(description="Listens to a rumor from Vizhay")
async def rumor(ctx):
	log("/ataraxia rumor")
	result = roll_intelligence_matrix(intelligence["ataraxia"][0])
	message = f"You pick up on a rumor in Vizhay: {result}"
	await ctx.respond(message)

@atrx_group.command(description="Encounter something in Dyatlov Pass")
async def encounter(ctx):
	log("/ataraxia encounter")
	result = roll_intelligence_matrix(intelligence["ataraxia"][1])
	message = f"During your travels through Dyatlov Pass, you run into: **{result}**"
	await ctx.respond(message)

bot.add_application_command(atrx_group)

hzfc_group = discord.SlashCommandGroup("hazfunction", "RATIONS #2: HAZARD FUNCTION Commands")

file = open('rations/hazard_function.json')
intelligence["hazfunction"] = json.load(file)
file.close()

@hzfc_group.command(description="Enter a new chamber")
async def room(ctx):
	log("/hazfunction room")
	result = roll_intelligence_matrix(intelligence["hazfunction"][0])
	await ctx.respond(result)

@hzfc_group.command(description="Spawn a chamber's hazard")
async def hazard(ctx):
	log("/hazfunction hazard")
	result = roll_intelligence_matrix(intelligence["hazfunction"][1])
	await ctx.respond(result)

@hzfc_group.command(description="Spawn a crucible animal")
async def animal(ctx):
	log("/hazfunction animal")
	result = roll_intelligence_matrix(intelligence["hazfunction"][4])
	await ctx.respond(result)

@hzfc_group.command(description="Spawn a chamber's encounter")
async def encounter(ctx, rooms_cleared: discord.Option(discord.SlashCommandOptionType.integer, "The number of rooms already cleared", required=True)):
	log(f"/hazfunction encounter {rooms_cleared}")
	if rooms_cleared < 0:
		await ctx.respond("Rooms cleared must be non-negative.",ephemeral=True)
		return
	options = intelligence["hazfunction"][2]["Values"]
	roll = d6() + rooms_cleared
	if roll > 16:
		roll = 16
	result = options[str(roll)]
	await ctx.respond(result)

@hzfc_group.command(description="Spawn a chamber's item")
async def item(ctx, rooms_cleared: discord.Option(discord.SlashCommandOptionType.integer, "The number of rooms already cleared", required=True)):
	log(f"/hazfunction item {rooms_cleared}")
	if rooms_cleared < 0:
		await ctx.respond("Rooms cleared must be non-negative.",ephemeral=True)
		return
	options = intelligence["hazfunction"][3]["Values"]
	roll = d6() + rooms_cleared
	if roll > 16:
		roll = 16
	result = options[str(roll)]
	await ctx.respond(result)

def hazfunc_codename():
	military_letter_codes = ["ALPHA", "BRAVO", "CHARLIE", "DELTA", "ECHO", "FOXTROT", "GOLF", "HOTEL", "INDIA", "JULIET", "KILO", "LIMA", "MIKE", "NOVEMBER", "OSCAR", "PAPA", "QUEBEC", "ROMEO", "SIERRA", "TANGO", "UNIFORM", "VICTOR", "WHISKEY", "XRAY", "YANKEE", "ZULU"]
	return f"{rnd.choice(military_letter_codes)}-{rnd.randint(0,9)}"

@hzfc_group.command(description="Produces a random Hazard Function character")
async def character(ctx):
	log(f"/hazfunction character")
	
	message = f"# {hazfunc_codename()}"
	message += "\nROLE: **SURVIVOR**\nDescribe why you want to live. If you live until the end of the mission, take another trait and gain a role, change your MAX HP to 6, then take a standard issue item, +1D6 MAX HP, or +1D6 WAR DICE.\n\n"
	
	traits = [rnd.choice(trait_data)]
	
	stats = {
		"MAX": d6(),
		"WAR": 0,
		"FORCEFUL": 0,
		"TACTICAL": 0,
		"CREATIVE": 0,
		"REFLEXIVE": 0
	}
	
	for trait in traits:
		bonus = trait["Stat"].split(" ")
		num = 0
		if bonus[1] in stats:
			if bonus[0] == "+1D6":
				num = d6()
			else:	
				num = 0
				numerical = bonus[0]
				if numerical[0] in ('+', '-'):
					num = int(numerical[1:])
					if numerical[0] == '-':
						num = -num
				else:
					num = int(numerical)
			
			stats[bonus[1]] += num
	
	message += f"MAX HP: {stats['MAX']}\n"
	message += f"WAR DICE: {stats['WAR']}\n\n"
	message += f"FORCEFUL: {stats['FORCEFUL']}\n"
	message += f"TACTICAL: {stats['TACTICAL']}\n"
	message += f"CREATIVE: {stats['CREATIVE']}\n"
	message += f"REFLEXIVE: {stats['REFLEXIVE']}\n\n"
	
	message += "TRAITS:\n"
	altmessage = message
	for trait in traits:
		message += f"- **{trait['Name']}** ({trait['Number']}): {trait['Effect']} ({trait['Stat']})\n"
		altmessage += f"- **{trait['Name']}** ({trait['Number']}, {trait['Stat']})\n"
	
	if len(message) > 2000:
		message = message.replace("FORCEFUL", "FRC")
		message = message.replace("CREATIVE", "CRE")
		message = message.replace("REFLEXIVE", "RFX")
		message = message.replace("TACTICAL", "TAC")
		message = message.replace("DAMAGE", "DMG")
		if len(message) > 2000:
			message = altmessage
	if len(message) > 2000:
		message = message.replace("FORCEFUL", "FRC")
		message = message.replace("CREATIVE", "CRE")
		message = message.replace("REFLEXIVE", "RFX")
		message = message.replace("TACTICAL", "TAC")
		message = message.replace("DAMAGE", "DMG")
		if len(message) > 2000:
			await ctx.respond("The generated character does not fit in the 2,000 character limit for messages. Try lowering the amount of traits.",ephemeral=True)
			return
	await ctx.respond(message)

bot.add_application_command(hzfc_group)

ctsh_group = discord.SlashCommandGroup("colony", "RATIONS #3: CULTURE SHOCK Commands")

file = open('rations/culture_shock.json')
intelligence["cultshock"] = json.load(file)
file.close()

def strain():
	symptom = roll_intelligence_matrix(intelligence["cultshock"][0])
	area = roll_intelligence_matrix(intelligence["cultshock"][1])
	return f"{symptom} {area}"

@ctsh_group.command(description="Provide a new Bacteria Canister from Colony's shop")
async def canister(ctx, amount: discord.Option(discord.SlashCommandOptionType.integer, "The number of rooms already cleared", required=False, default=1)):
	log(f"/colony canister {amount}")
	if amount < 1:
		await ctx.respond("Canisters provided must be 1 or more.",ephemeral=True)
	elif amount > 15:
		await ctx.respond("Canisters provided must be 15 or less.",ephemeral=True)
	elif amount == 1:
		await ctx.respond(f"Colony offers you a Bacteria Canister that's labelled... **{strain()}**. Whatever that means.")
	else:
		msg = "Colony offers you several Bacteria Canisters:"
		for i in range(amount):
			msg += f"\n- **{strain()}**"
		await ctx.respond(msg)

@ctsh_group.command(description="Roll to see if Colony will spawn.")
async def spawn(ctx):
	log(f"/colony spawn")
	if d6() % 2 == 1:
		await ctx.respond("Colony **will** spawn in this region.")
	else:
		await ctx.respond("Colony **will not** spawn in this region.")

bot.add_application_command(ctsh_group)

log("Starting bot session")
bot.run(token)