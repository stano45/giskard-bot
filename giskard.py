import discord
from discord.ext import commands
from reddit import RedditScraper
import prawcore
from datetime import datetime
import config as cfg
import twitch_scrape as twitch
import youtube_dl
import asyncio


ytdl_format_options = {
	'format': 'bestaudio/best',
	'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
	'restrictfilenames': True,
	'noplaylist': True,
	'nocheckcertificate': True,
	'ignoreerrors': False,
	'logtostderr': False,
	'quiet': True,
	'no_warnings': True,
	'default_search': 'auto',
	'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
	'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
	def __init__(self, source, *, data, volume=0.5):
		super().__init__(source, volume)

		self.data = data

		self.title = data.get('title')
		self.url = data.get('webpage_url')
		self.duration = data.get('duration')

	@classmethod
	async def from_url(cls, url, *, loop=None, stream=False):
		loop = loop or asyncio.get_event_loop()
		data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

		if 'entries' in data:
			# take first item from a playlist
			data = data['entries'][0]

		filename = data['url'] if stream else ytdl.prepare_filename(data)
		return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music(commands.Cog):
   
	def __init__(self, bot):
		self.bot = bot

	@commands.command(
		name = 'play',
		description = "!play [video name or url] -- plays video sound in channel you're currently in")
	async def play(self, ctx):
		"""--plays sound from youtube video"""
		url = ctx.message.content[6:]
		if ctx.voice_client is None:
			if ctx.author.voice:
				await ctx.author.voice.channel.connect()
				await ctx.voice_client.disconnect()
				await ctx.author.voice.channel.connect()
			else:
				await message.edit(content = "You are not connected to a voice channel")
				raise commands.CommandError("Author not connected to a voice channel")
		elif ctx.voice_client.is_playing():
			ctx.voice_client.stop()
		async with ctx.typing():
			player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
			ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
		await ctx.send('Now playing: {}\nDuration: {} seconds\nURL: {}'.format(player.title, player.duration, player.url))
		
	@commands.command(
		name = 'stop',
		description = '!stop -- stops the current playback')
	async def stop(self, ctx):
		"""--stops current playback"""
		await ctx.send("Playback stopped")
		await ctx.voice_client.disconnect()

	@commands.command(
		name = 'volume',
		description = '!volume [int 0-100] -- changes the volume to the value')
	async def volume(self, ctx, volume: int):
		"""--hanges the player's volume"""
		if ctx.voice_client is None:
			return await ctx.send("Not connected to a voice channel")

		ctx.voice_client.source.volume = volume / 100
		await ctx.send("Changed volume to {}%".format(volume))

class Websites(commands.Cog):
	def __init__(self,bot):
		self.bot = bot

	@commands.command(
		name = 'islive',
		description = '!islive [streamer_name] -- checks if a given streamer is online')
	async def is_live(self, ctx):
		"""--checks if a given streamer is online."""
		channel = ctx.message.content[8:]
		info = twitch.is_live(channel)
		if info:
			msg = info.user_name + " is live with " + str(info.viewer_count) + " viewers: \n" + info.title + "\n@ https://twitch.tv/" + info.user_name   
		else:
			msg = channel + " is offline at the moment"
		await ctx.send(msg)

	@commands.command(
		name = 'rhot',
		description = '!rhot [subreddit] -- finds #1 hot post from subreddit that isn\'t stickied')
	async def rhot(self, ctx):
		"""--finds #1 hot post from subreddit that isn't stickied."""
		reddit = RedditScraper()
		subreddit = ctx.message.content[6:]
		submission = reddit.get_top_submission(subreddit)
		if submission:
			ts = submission.created_utc
			msg = "Posted at: " + datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S') + '\n' + submission.title + '\n' + submission.url
			await ctx.send("This is the #1 hot post from " + subreddit + ": \n" + msg)
		else:
			await ctx.send("Subreddit is private, or has not been found")


token = cfg.discord_token
bot = commands.Bot(command_prefix='!')

@bot.event
async def on_message(message):
	print(message.content)
	await bot.process_commands(message)

@bot.event
async def on_ready():
	print("ready")
	ch = bot.get_channel(488013635432742916)
	await ch.send("Giskard online! Type !help for more info")


bot.add_cog(Music(bot))
bot.add_cog(Websites(bot))

bot.run(token)