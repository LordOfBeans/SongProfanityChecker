from genius_client import GeniusClient
from db_client import DatabaseClient
from profanity_detection import ProfanityClient, OVERLAP_TYPES
from menu_utils import pickInteger, spacePadString

class LyricsCli:
	
	def __init__(self, db_cur, genius):
		self.db_cur = db_cur
		self.genius = genius
		self.checker = ProfanityClient(
			self.db_cur.fetchPhraseListByDetection('concatenation'),
			self.db_cur.fetchPhraseListByDetection('isolation'),
			self.db_cur.fetchPhraseListByDetection('subword'),
			self.db_cur.fetchProfanityLevelDict(),
			self.db_cur.fetchLevelPenaltyDict()
		)
		self.PENALTY_MAXIMUM = 12
		self.SPACE_PADDING = 4
	
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
		print('1. Scrape Lyrics for All Tracks')
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
				pageviews = 0
				if 'pageviews' in track['song']['stats']:
					pageviews = track['song']['stats']['pageviews']
				self.db_cur.addSong(track_id, track_title, lyrics_path, pageviews)
				print(f'Scraping lyrics for {track_title}')
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
	
	def artistOptionsMenu(self, artist_id, artist_name):
		print(f'\nARTIST OPTIONS for {artist_name}')
		print('0. Go Back')
		print('1. Scrape Lyrics for All Songs')
		choice = pickInteger(0, 1)
		if choice == 0:
			return
		else:
			page = 1
			while page is not None:
				resp = self.genius.getArtistSongs(artist_id, page=page)
				songs = resp['songs']
				for song in songs:
					song_id = song['id']	
					song_title = song['title']
					lyrics_path = song['path']
					pageviews = 0
					if 'pageviews' in song['stats']:
						pageviews = song['stats']['pageviews']
					self.db_cur.addSong(song_id, song_title, lyrics_path, pageviews)
					print(f'Scraping lyrics for {song_title}')
					if self.db_cur.checkSongHasLyrics(song_id):
						print(f'Already scraped lyrics for {song_title}')
					elif song['lyrics_state'] != 'complete':
						print(f'Skipped {song_title} due to incomplete lyrics')
					else:
						lyrics = self.genius.scrapeSongLyrics(lyrics_path)
						self.db_cur.addSongLyrics(song_id, lyrics)
					for artist in song['primary_artists']:
						song_artist_id = artist['id']
						song_artist_name = artist['name']
						self.db_cur.addArtist(song_artist_id, song_artist_name)
						self.db_cur.addArtistToSong(song_artist_id, song_id)	
					self.db_cur.addArtistToSong(artist_id, song_id) # If I'm searching for an artist's songs, I probably also want them to be referenced for songs they're featured on
				print(f'Committing page {page} of popular {artist_name} songs to database')
				self.db_cur.commit()
				page = resp['next_page']	

	def songOptionsMenu(self, song_id):
		song_data = self.genius.getSongData(song_id)
		song_title = song_data['full_title']
		while True:
			print(f'\nSONG OPTIONS for {song_title}')
			print('0. Go Back')
			print('1. Download Song Lyrics')
			album = song_data['album']
			if album is not None:
				album_title = album['name']
				print(f'2. Go to Album: {album_title}')
			artists = song_data['primary_artists']
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
				chosen_artist = artists[choice-3]
				artist_id = chosen_artist['id']
				artist_name = chosen_artist['name']
				self.artistOptionsMenu(artist_id, artist_name)

	def investigateSongReportMenu(self, song_id, song_name, report):
		print(f'\nSONG PROFANITY REPORT for {song_name}')
		string_rep = report.toString(self.SPACE_PADDING)
		print(string_rep)
		input('Press enter to return: ')
		

	def profanityCheckAlbumMenu(self, album_id, album_title):
		album_tracks = sorted(self.db_cur.fetchAlbumSongs(album_id), key=lambda x: x[5] if x[5] is not None else 4096)
		while True:
			print(f'\nALBUM PROFANITY REPORT for {album_title}')
			print('0. Go Back')
			reports = []
			for track in album_tracks:
				number = track[5]
				song_id = track[0]
				title = track[1]
				lyrics = track[2]
				lyrics_path = track[3]
				pageviews = track[4]
				print(f'{number}. {title}')
				report = self.checker.checkLyrics(lyrics)
				reports.append(report)
				report_dict = report.getProfanityCounts()
				total_penalty = report_dict['total_penalty']
				penalty_str = str(total_penalty)
				if total_penalty <= self.PENALTY_MAXIMUM:
					penalty_str += ' PASSES!'
				profanities = list(report_dict['profanities'].keys())
				profanities_str = ', '.join(profanities)
				print(spacePadString(f'Penalty Total: {penalty_str}', self.SPACE_PADDING))
				print(spacePadString(f'Profanities: {profanities_str}', self.SPACE_PADDING))
				print(spacePadString(f'Pageviews: {pageviews}', self.SPACE_PADDING))
				print(spacePadString(f'Lyrics At: https://genius.com{lyrics_path}', self.SPACE_PADDING))
			choice = pickInteger(0, len(album_tracks))
			if choice == 0:
				return
			else:
				song_choice = album_tracks[choice-1]
				song_name = song_choice[1]
				song_id = song_choice[0]
				song_report = reports[choice-1]
				self.investigateSongReportMenu(song_id, song_name, song_report)

	def chooseAlbumCheckMenu(self):
		while True:
			print('\nCHOOSE ALBUM FOR PROFANITY CHECK')
			print('0. Go Back')
			albums = self.db_cur.fetchAllAlbums()
			i = 0
			for album_id, title in albums:
				i += 1
				print(f'{i}. {title}')
			choice = pickInteger(0, len(albums))
			if choice == 0:
				return
			else:
				album_choice = albums[choice - 1]
				self.profanityCheckAlbumMenu(album_choice[0], album_choice[1])

	def profanityCheckArtistMenu(self, artist_id, artist_name):
		artist_songs = sorted(self.db_cur.fetchArtistSongs(artist_id), key=lambda x: x[4], reverse=True)
		while True:
			print(f'\nARTIST SONGS PROFANITY REPORT for {artist_name}')
			print('0. Go Back')
			reports = []
			i = 0
			for song in artist_songs:
				i += 1
				lyrics = song[2]
				if lyrics is None:
					continue
				report = self.checker.checkLyrics(lyrics)
				reports.append(report)
				report_dict = report.getProfanityCounts()
				total_penalty = report_dict['total_penalty']
				if total_penalty <= self.PENALTY_MAXIMUM:
					song_title = song[1]
					lyrics_path = song[3]
					pageviews = song[4]
					profanities = list(report_dict['profanities'].keys())
					profanities_str = ', '.join(profanities)
					print(f'{i}. {song_title}')
					print(spacePadString(f'Penalty Total: {total_penalty}', self.SPACE_PADDING))
					print(spacePadString(f'Profanities: {profanities_str}', self.SPACE_PADDING))
					print(spacePadString(f'Pageviews: {pageviews}', self.SPACE_PADDING))
					print(spacePadString(f'Lyrics At: https://genius.com{lyrics_path}', self.SPACE_PADDING))
			choice = pickInteger(0, len(reports))
			if choice == 0:
				return
			else:
				chosen_song = artist_songs[choice - 1]
				song_id = chosen_song[0]
				song_name = chosen_song[1]
				song_report = reports[choice - 1]
				self.investigateSongReportMenu(song_id, song_name, song_report)

	def chooseArtistCheckMenu(self):
		while True:
			print('\nCHOOSE ARTIST FOR PROFANITY CHECK')
			print('0. Go Back')
			artists = sorted(self.db_cur.fetchAllArtists(), key=lambda x: x[1])
			i = 0
			for artist_id, name in artists:
				i += 1
				print(f'{i}. {name}')
			choice = pickInteger(0, len(artists))
			if choice == 0:
				return
			else:
				artist_choice = artists[choice - 1]
				self.profanityCheckArtistMenu(artist_choice[0], artist_choice[1])

	def profanityCheckMenu(self):
		while True:
			print('\nPROFANITY CHECK VARIETIES')
			print('0. Go Back')
			print('1. Check Albums')
			print('2. Check by Artist')
			choice = pickInteger(0, 2)
			if choice == 0:
				return
			elif choice == 1:
				self.chooseAlbumCheckMenu()
			elif choice == 2:
				self.chooseArtistCheckMenu()

	def  pasteAlbumMenu(self):
		url = input('Paste album URL: ')
		print('Scraping page for the album ID')
		album_id, album_title = self.genius.scrapeAlbumData(url)	
		self.albumOptionsMenu(album_id, album_title)

	def pasteArtistMenu(self):
		url = input('Past artist URL: ')
		print('Scraping page for the artist ID')
		artist_id, artist_name = self.genius.scrapeArtistData(url)	
		self.artistOptionsMenu(artist_id, artist_name)

	def scrapeLyricsMenu(self):
		while True:
			print('\nSCRAPE LYRICS OPTIONS')
			print('0. Go Back')
			print('1. Genius Song Search')
			print('2. Paste Album URL')
			print('3. Paste Artist URL')
			choice = pickInteger(0, 3)
			if choice == 0:
				return
			elif choice == 1:
				track = self.songSearchMenu()
				if track is None:
					continue
				self.songOptionsMenu(track)
			elif choice == 2:
				self.pasteAlbumMenu()
			elif choice == 3:
				self.pasteArtistMenu()
	
	def mainMenu(self):
		while True:
			print('\nMAIN MENU')
			print('0. Quit and Commit')
			print('1. Scrape Song Lyrics')
			print('2. Profanity Check')
			print('3. Clear All Music')
			choice = pickInteger(0, 3)
			if choice == 0:
				self.db_cur.commit()
				break
			elif choice == 1:
				self.scrapeLyricsMenu()
			elif choice == 2:
				self.profanityCheckMenu()
			elif choice == 3:
				self.db_cur.clearAllMusic()

def main():
	with GeniusClient('secret.json') as genius, DatabaseClient('database.db') as db_cur:
		lyrics_cli = LyricsCli(db_cur, genius)
		lyrics_cli.mainMenu()

if __name__ == '__main__':
	main()
