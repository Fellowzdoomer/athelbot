import os
import random
import asyncio
import urllib.request
import ftplib

import discord
from discord import Member
from discord import Game
from discord.ext import commands
from discord.ext.commands import Bot
from discord import Permissions

# Initialize quotes
quotes = []
quotes_addedby = []
quote_display = "";

# FTP
ftp_server = os.environ['FTP_SERVER']
ftp_username = os.environ['FTP_USER']
ftp_password = os.environ['FTP_PASS']


print ("Connecting to FTP...");
ftp_connection = ftplib.FTP(ftp_server,ftp_username,ftp_password);
remote_path="/";
ftp_connection.cwd(remote_path);
print("Getting quotes...");
if "ab_quotes.txt" in ftp_connection.nlst():	
	ftp_connection.retrbinary('RETR ab_quotes.txt', open('ab_quotes.txt', 'wb').write)
if "ab_quotes_addedby.txt" in ftp_connection.nlst():
	ftp_connection.retrbinary('RETR ab_quotes_addedby.txt', open('ab_quotes_addedby.txt', 'wb').write)
print("Done downloading!")

# Load and append Quotes
if os.path.exists("ab_quotes.txt"):
	with open("ab_quotes.txt") as f:
		for line in f:
			line = line.strip()
			quotes.append(line)

# Load and append Quotes-Addedby
if os.path.exists("ab_quotes_addedby.txt"):
	with open("ab_quotes_addedby.txt") as f:
		for line in f:
			line = line.strip()
			quotes_addedby.append(line)
print("Quotes appended! Starting bot...");

# Standard bot setup
BOT_PREFIX = "a-";
TOKEN = os.environ['BOT_TOKEN']

mod_id = os.environ['MOD_ROLE_ID']
owner_id = os.environ['OWNER_ROLE_ID']

client = Bot(command_prefix = BOT_PREFIX);
client.remove_command('help');


# Bot is ready.
@client.event
async def on_ready():
    print ("Initializing...");
    print ("Started.");

# Command
@client.command()
async def help(ctx):
	#await ctx.author.send("sneed")
	em = discord.Embed(title="AthelBot Notification",
					   description = "This command is WIP.",
					   color = 0x00ffff)
	await ctx.send(embed=em)

@client.command()
async def about(ctx):
	channel = ctx.message.channel
	em = discord.Embed(title="About AthelBot!",
					   description = "AthelBot is my own little servant bot / side project of mine. It was originally made for me to store quotes, but has since turned into a multiuse bot. 'a-help' will get you all the commands available!",
					   color = 0x00ffff)
	await ctx.send(embed=em)

# Add quote
@client.command(pass_context=True)
async def addquote(ctx, *, quoteAdd: str = None):
	if quoteAdd is None:
		await ctx.send("You have to type out the quote you want added!")
	else:
		quote_embed = discord.Embed(title="Quote Added!",
								description = quoteAdd,
								color = 0x00ffff)
		quote_embed.set_footer(text="Quote added by " + str(ctx.author))
		quotes_addedby.append(str(ctx.author))
		quotes.append(str(quoteAdd));
		await ctx.send(embed=quote_embed)

# Quote
@client.command(pass_context=True)
async def quote(ctx, number: int = None):
	if number is None:
		number = random.randint(1,len(quotes)-1);
		quote_embed = discord.Embed(title="Quote",
								description = quotes[number],
								color = 0x00ffff)
		quote_embed.set_footer(text="Quote added by " + str(quotes_addedby[number]) + ". Quote " + str(number) + " of " + str(len(quotes)-1))
		await ctx.send(embed=quote_embed)
	elif number <= 0 or number > len(quotes):
		await ctx.send("Not a valid quote ID!");
	else:
		try:
			quote_embed = discord.Embed(title="Quote",
									description = quotes[number],
									color = 0x00ffff)
			quote_embed.set_footer(text="Quote added by " + str(quotes_addedby[number]) + ". Quote " + str(number) + " of " + str(len(quotes)-1))
			await ctx.send(embed=quote_embed)
		except IndexError:
			await ctx.send("Not a valid quote ID!")

# List quotes
@client.command()
async def listquote(ctx):
	await ctx.send("A list of all the quotes will be sent to your DMs.")
	await ctx.author.send(quotes)

# Delete a quote
@client.command(pass_context=True)
async def delquote(ctx, number: int = None):
	if mod_id in [y.id for y in ctx.message.author.roles] or owner_id in [y.id for y in ctx.message.author.roles]:
		if number is None:
			await ctx.send("Please specify what quote you want deleted.")
		elif number <= 0 or number > len(quotes)-1:
			await ctx.send("Not a valid quote ID!")
		else:
			try:
				quotes.pop(number)
				quotes_addedby.pop(number)
				await ctx.send("Quote deleted!")
			except IndexError:
				await ctx.send("Not a valid quote ID!")
	else:
		await ctx.send("Sorry, but you do not have the appropriate role to perform this action. You need to be a moderator, at least.")
        
client.run(TOKEN);

# When the bot shuts down.
print("Saving quotes...");
if os.path.exists("ab_quotes.txt"):
	os.remove("ab_quotes.txt")
if os.path.exists("ab_quotes_addedby.txt"):
	os.remove("ab_quotes_addedby.txt")

f = open("ab_quotes.txt", "w+")
f_by = open("ab_quotes_addedby.txt", "w+")

'''f.write("-- Null Quote ID: 0\n");
f_by.write("-- Null Quote ID: 0\n");'''

for item in quotes:
	f.write("%s\n" % item);
for item in quotes_addedby:
	f_by.write("%s\n" % item);

f.close();
f_by.close();

print("Uploading to FTP server...");

ftp_connection.storbinary('STOR ab_quotes.txt', open('ab_quotes.txt', 'rb'));
ftp_connection.storbinary('STOR ab_quotes_addedby.txt', open('ab_quotes_addedby.txt', 'rb'));
print("Closing connection.");
ftp_connection.quit();


print("Success!");
print("Terminated script.");