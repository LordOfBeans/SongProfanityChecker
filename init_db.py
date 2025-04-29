import sqlite

DB_FILE = 'database.db'

def main():
	conn = sqlite3.connect(DB_FILE)
	cur = conn.cursor()

	cur.execute("""
		CREATE TABLE IF NOT EXISTS artists (
			artist_id INT PRIMARY KEY,
			name TEXT NOT NULL
		)
	""")
	
	cur.execute("""
		CREATE TABLE IF NOT EXISTS albums (
			album_id INT PRIMARY KEY,
			title TEXT NOT NULL
		)
	""")

	# TODO: Investigate primary artist column if that's a fairly universal genius feature
	cur.execute("""
		CREATE TABLE IF NOT EXISTS songs (
			song_id INT PRIMARY KEY,
			title TEXT NOT NULL,
			lyrics TEXT DEFAULT NULL
		)
	""")

	# Best way I can find to add or remove columns from a table w/o getting rid of whole table
	res = cur.execute("""
		PRAGMA TABLE_INFO(songs)
	""")
	columns = res.fetchall()
	column_names = []
	for column_info in columns:
		column_names.append(column_info[1])
	if 'lyrics_path' not in column_names:
		cur.execute("""
			ALTER TABLE songs
			ADD COLUMN lyrics_path TEXT DEFAULT NULL
		""")
	if 'pageviews' not in column_names:
		cur.execute("""
			ALTER TABLE songs
			ADD COLUMN pageviews INT DEFAULT 0
		""")

	cur.execute("""
		CREATE TABLE IF NOT EXISTS album_songs (
			album_id INT,
			song_id INT,
			track_number INT,
			PRIMARY KEY (album_id, song_id)
		)
	""")

	cur.execute("""
		CREATE TABLE IF NOT EXISTS song_artists (
			song_id INT,
			artist_id INT,
			PRIMARY KEY (song_id, artist_id)
		)
	""")

	cur.execute("""
		CREATE TABLE IF NOT EXISTS profanities (
			phrase TEXT PRIMARY KEY,
			level TEXT DEFAULT NULL,
			detection TEXT DEFAULT NULL
		)
	""")

	cur.execute("""
		CREATE TABLE IF NOT EXISTS profanity_levels (
			level TEXT PRIMARY KEY,
			points INT DEFAULT 1
		)
	""")

if __name__ == '__main__':
	main()
