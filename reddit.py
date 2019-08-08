import praw
import prawcore
import config as cfg
 

class RedditScraper:

	def __init__(self):
		self.reddit = praw.Reddit(client_id=cfg.reddit_info['client_id'],
                     client_secret=cfg.reddit_info['client_secret'],
                     user_agent=cfg.reddit_info['user_agent'])
		if self.reddit.read_only == True:
			print("Auth successful.")
		else:
			print("Auth error")
	
	def get_top_submission(self, subreddit_name):
		try:
			if subreddit_name.startswith("r/"):
				subreddit_name = subreddit_name[2:]
			print("attempting to search in: ", subreddit_name)
			subreddit = self.reddit.subreddit(subreddit_name)
			hot_posts = subreddit.hot(limit = 5)
			for submission in hot_posts:
				if not submission.stickied:
					return submission
		except prawcore.exceptions.Forbidden:
			print("exception: Fobidden - subreddit private")
		except prawcore.exceptions.Redirect:
			print("exception: Redirect - subreddit doesnt exist")
		except prawcore.exceptions.BadRequest:
			print("exception: BadRequest - bad request (remove /r)")
		else:
			print("Subreddit found.")
		