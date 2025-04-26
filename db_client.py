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

	def clearAllProfanities(self):
		self.cur.execute("""
			DELETE FROM profanities;
		""")

	def addSong(self, song_id, title):
		self.cur.execute("""
			INSERT OR IGNORE INTO songs (song_id, title)
			VALUES (?, ?)
		""", [song_id, title])

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
