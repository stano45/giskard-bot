import discord
from reddit import RedditScraper
import prawcore
from datetime import datetime
import config as cfg
import twitch_scrape as twitch

token = cfg.discord_token

client = discord.Client()

@client.event
async def on_ready():
    print("ready")
    ch = client.get_channel(488013635432742916)
    await ch.send("Giskard online! Type !help for more info.")


@client.event
async def on_message(message):
    print(message.content)
    if (message.author == client.user):
        return

    if message.content.startswith("!help"):
        msg = "Commands: \n" + "!rhot [subreddit] -- finds #1 hot post from subreddit that isn't stickied.\n"\
        					 + "!islive [streamer_name] -- checks if a given streamer is online.\n"
        await message.channel.send(msg)

    if message.content.startswith("!rhot"):
        reddit = RedditScraper()
        subreddit = message.content[6:]
        submission = reddit.get_top_submission(subreddit)
        if submission:
            ts = submission.created_utc
            msg = "Posted at: " + datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S') + '\n' + submission.title + '\n' + submission.url
            await message.channel.send("This is the #1 hot post from " + subreddit + ": \n" + msg)
        else:
            await message.channel.send("Sorry! Subreddit is private, or has not been found.")

    if message.content.startswith("!islive"):
    	channel = message.content[8:]
    	info = twitch.is_live(channel)
    	if info:
    		msg = "Streamer is live @ " + info
    	else:
    		msg = "Streamer is offline at the moment."
    	await message.channel.send(msg)



client.run(token)