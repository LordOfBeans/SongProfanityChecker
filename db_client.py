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

	def fetchAllSongs(self):
		self.cur.execute("""
			SELECT * FROM songs	
		""")
		return self.cur.fetchall()
