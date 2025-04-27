from genius_client import GeniusClient
from db_client import DatabaseClient
from profanity_detection import ProfanityClient, OVERLAP_TYPES

class LyricsCli:
	
	def __init__(self, db_cur, genius):
		self.db_cur = db_cur
		self.genius = genius	
	
	def start(self):
		

def main():
	with GeniusClient('secret.json') as genius, DatabaseClient('database.db') as db_cur:
		lyrics_cli = LyricsCli(db_cur, genius)
		lyrics_cli.start()	

if __name__ = '__main__':
	main()
