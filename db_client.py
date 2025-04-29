import sqlite3

class DatabaseClient:
	def __init__(self, db_file):
		self.db_file = db_file
		self.conn = None
		self.cur = None

	def __enter__(self):
		self.conn = sqlite3.connect(self.db_file)
		self.cur = self.conn.cursor()
		return self

	def __exit__(self, exc_type, exc_value, tracebrack):
		self.conn.close()

	def commit(self):
		self.conn.commit()

	def addArtist(self, artist_id, name):
		self.cur.execute("""
			INSERT OR IGNORE INTO artists (artist_id, name)
			VALUES (?, ?)
		""", [artist_id, name])

	def addAlbum(self, album_id, title):
		self.cur.execute("""
			INSERT OR IGNORE INTO albums (album_id, title)
			VALUES (?, ?)
		""", [album_id, title])

	def addSong(self, song_id, title, lyrics_path, pageviews):
		self.cur.execute("""
			INSERT OR IGNORE INTO songs (song_id, title, lyrics_path, pageviews)
			VALUES (?, ?, ?, ?)
		""", [song_id, title, lyrics_path, pageviews])

	def addSongToAlbum(self, song_id, album_id, track_number):
		self.cur.execute("""
			INSERT OR IGNORE INTO album_songs (album_id, song_id, track_number)
			VALUES (?, ?, ?)
		""", [album_id, song_id, track_number])

	def addArtistToSong(self, artist_id, song_id):
		self.cur.execute("""
			INSERT OR IGNORE INTO song_artists (song_id, artist_id)
			VALUES (?, ?)
		""", [song_id, artist_id])
		

	def addSongLyrics(self, song_id, lyrics):
		self.cur.execute("""
			UPDATE songs
			SET lyrics = ?
			WHERE song_id = ?
		""", [lyrics, song_id])

	def addProfanityLevel(self, name, points):
		self.cur.execute("""
			INSERT INTO profanity_levels (level, points)
			VALUES (?, ?)
		""", [name, points])

	def addProfanity(self, phrase, level, detection):
		self.cur.execute("""
			INSERT INTO profanities (phrase, level, detection)
			VALUES (?, ?, ?)
		""", [phrase, level, detection])

	def fetchAllAlbums(self):
		self.cur.execute("""
			SELECT * FROM albums
		""")
		return self.cur.fetchall()

	def fetchAlbumSongs(self, album_id):
		self.cur.execute("""
			SELECT song_id, title, lyrics, lyrics_path, pageviews, track_number
			FROM album_songs NATURAL JOIN songs
			WHERE album_id = ?
		""", [album_id])
		return self.cur.fetchall()

	def fetchAllSongs(self):
		self.cur.execute("""
			SELECT * FROM songs	
		""")
		return self.cur.fetchall()

	def fetchLevelPenaltyDict(self):
		self.cur.execute("""
			SELECT level, points FROM profanity_levels
		""")
		return_dict = {}
		for item in self.cur.fetchall():
			level = item[0]
			points = item[1]
			return_dict[level] = points
		return return_dict

	def fetchPhraseListByDetection(self, detection):
		self.cur.execute("""
			SELECT phrase FROM profanities
			WHERE detection = ?
		""", [detection])
		phrase_list = []
		for item in self.cur.fetchall():
			phrase_list.append(item[0])
		return phrase_list

	def fetchProfanityLevelDict(self):
		self.cur.execute("""
			SELECT phrase, level FROM profanities
		""")
		phrase_dict = {}
		for item in self.cur.fetchall():
			phrase = item[0]
			level = item[1]
			phrase_dict[phrase] = level
		return phrase_dict

	def fetchAllProfanities(self):
		self.cur.execute("""
			SELECT * FROM profanities
		""")
		return self.cur.fetchall()

	# TODO: Delete from more tables as I add more tables
	def clearAllMusic(self):
		self.cur.executescript("""
			DELETE FROM artists;
			DELETE FROM albums;
			DELETE FROM songs;
			DELETE FROM album_songs;
			DELETE FROM song_artists 
		""")

	def clearAllProfanities(self):
		self.cur.execute("""
			DELETE FROM profanities
		""")
