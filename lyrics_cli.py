from genius_client import GeniusClient
from db_client import DatabaseClient
from profanity_detection import ProfanityClient, OVERLAP_TYPES
from menu_utils import pickInteger, spacePadString

class LyricsCli:
	
	def __init__(self, db_cur, genius):
		self.db_cur = db_cur
		self.genius = genius	
	
	def songSearchMenu(self):
		print('\nGENIUS SONG SEARCH')
		title = input('Enter a song title: ')
		if title.strip() == '':
			print('Genius song search cancelled')
			return None
		hits = self.genius.songSearch(title)
		print(f'Found {len(hits)} results')
		print('0. Go Back')
		for i in range(0, len(hits)):
			curr_hit = hits[i]['result']
			full_title = curr_hit['full_title']
			print(f'{i+1}. {full_title}')
		choice = pickInteger(0, len(hits))
		if choice == 0:
			return None
		else:
			return hits[choice-1]['result']['id']

	def albumOptionsMenu(self, album_id, album_title):
		album_tracks = self.genius.getAlbumTracks(album_id)
		print(f'\nALBUM OPTIONS for {album_title}')
		print('0. Go Back')
		print('1. Download Lyrics for All Tracks')
		choice = pickInteger(0, 1)
		if choice == 0:
			return
		elif choice == 1:
			self.db_cur.addAlbum(album_id, album_title)
			for track in album_tracks:
				track_number = track['number'] # Where track appears in album order
				lyrics_path = track['song']['path']
				track_title = track['song']['title']
				track_id = track['song']['id']
				pageviews = track['song']['stats']['pageviews']
				self.db_cur.addSong(track_id, track_title, lyrics_path, pageviews)
				print(f'Downloading lyrics for {track_title}')
				lyrics = self.genius.scrapeSongLyrics(lyrics_path)
				self.db_cur.addSongLyrics(track_id, lyrics)
				self.db_cur.addSongToAlbum(track_id, album_id, track_number)
				track_artists = track['song']['primary_artists']
				for artist in track_artists:
					artist_id = artist['id']
					artist_name = artist['name']
					self.db_cur.addArtist(artist_id, artist_name)
					self.db_cur.addArtistToSong(artist_id, track_id)
			print(f'Committing {album_title} to database')
			self.db_cur.commit()	
	
	def songOptionsMenu(self, song_id):
		song_data = self.genius.getSongData(song_id)
		song_title = song_data['full_title']
		while True:
			print(f'\nSONG OPTIONS for {song_title}')
			print('0. Go Back')
			print('1. Download Song Lyrics')
			album = song_data['album']
			album_title = album['name']
			print(f'2. Go to Album: {album_title}')
			artists = album['primary_artists']
			for i in range(0, len(artists)):
				curr_artist_name = artists[i]['name']
				print(f'{i+3}. Go to Artist: {curr_artist_name}')
			choice = pickInteger(0, len(artists) + 3)
			if choice == 0:
				return
			elif choice == 1:
				return
			elif choice == 2:
				album_id = album['id']
				self.albumOptionsMenu(album_id, album_title)
			else:
				return

	def mainMenu(self):
		while True:
			print('\nMAIN MENU')
			print('0. Quit and Commit')
			print('1. Genius Song Search')
			print('2. Profanity Search')
			print('3. Clear All Music')
			choice = pickInteger(0, 3)
			if choice == 0:
				self.db_cur.commit()
				break
			elif choice == 1:
				track = self.songSearchMenu()
				if track is None:
					continue
				self.songOptionsMenu(track)
			elif choice == 3:
				self.db_cur.clearAllMusic()

def main():
	with GeniusClient('secret.json') as genius, DatabaseClient('database.db') as db_cur:
		lyrics_cli = LyricsCli(db_cur, genius)
		lyrics_cli.mainMenu()

if __name__ == '__main__':
	main()
