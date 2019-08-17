from twitch.helix.api import TwitchHelix
import config as cfg

def is_live (channel):
	helix = TwitchHelix(client_id = cfg.twitch_id)
	info = helix.get_streams(user_logins = channel)
	print(info)
	if info.__len__() > 0:
		return "https://twitch.tv/" + info[0].user_name
	else:
		return None
	
