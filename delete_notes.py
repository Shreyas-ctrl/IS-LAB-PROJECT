import sqlite3

# Connect to database
conn = sqlite3.connect('notes.db')
cursor = conn.cursor()

# Delete all notes
cursor.execute('DELETE FROM note')

# IMPORTANT: Commit the changes
conn.commit()

# Close connection
conn.close()

print('All notes deleted successfully!')
