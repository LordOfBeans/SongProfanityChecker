import sqlite3

DB_FILE = 'database.db'

def main():
	conn = sqlite3.connect(DB_FILE)
	cur = conn.cursor()
	
	cur.execute("""
		CREATE TABLE IF NOT EXISTS albums (
			album_id INT PRIMARY KEY,
			title TEXT NOT NULL
		)
	""")

	cur.execute("""
		CREATE TABLE IF NOT EXISTS songs (
			song_id INT PRIMARY KEY,
			title TEXT NOT NULL,
			lyrics TEXT DEFAULT NULL
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
