from __future__ import unicode_literals
import youtube_dl
import os

def download_song(song_title, target):
	
	"""
	Download a song using youtube url and song title
	"""

	song_url = "ytsearch1:" + song_title

	ydl_opts = {
		'outtmpl' : 'C:/Users/Uzivatel/Desktop/bot/songs/{}.%(ext)s'.format(song_title),
		'format': 'bestaudio/best',
		'postprocessors': [
			{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3',
			 'preferredquality': '192',
			}
		]
	}

	for file in os.listdir(target):
		filename = os.fsdecode(file)
		if filename == song_title + ".mp3":
			print("File already cached, downloading metadata...") 
			try:
				with youtube_dl.YoutubeDL(ydl_opts) as ydl:
					info_dict = ydl.extract_info(song_url, download=False) 
			except youtube_dl.utils.DownloadError:
				print("Video not found")
				return None
			else:
				print("Metadata downloaded, returning...") 
				return info_dict

	try:
		with youtube_dl.YoutubeDL(ydl_opts) as ydl:
			info_dict = ydl.extract_info(song_url, download=True) 
	except youtube_dl.utils.DownloadError:
		print("Video not found")
		return None
	else:
		return info_dict
	