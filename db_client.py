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

	def fetchAllSongs(self):
		self.cur.execute("""
			SELECT * FROM songs	
		""")
		return self.cur.fetchall()

	def fetchProfanityLevels(self):
		self.cur.execute("""
			SELECT * FROM profanity_levels
		""")
		return self.cur.fetchall()

	def fetchAllProfanities(self):
		self.cur.execute("""
			SELECT * FROM profanities
		""")
		return self.cur.fetchall()

	# TODO: Delete from more tables as I add more tables
	def clearAllMusic(self):
		self.cur.execute("""
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


