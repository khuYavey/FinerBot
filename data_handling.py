import sqlite3

'''local.db'''

def init_local():
    conn = sqlite3.connect("local.db")
    cursor = conn.cursor()

    # Create a table to store user data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            photo_id TEXT,
            photo_itself BLOB,
            latitude REAL,
            longitude REAL,
            timestamp DATETIME
        )
    ''')

    conn.commit()
    conn.close()
def delete_from_db(user_id):
    conn = sqlite3.connect("local.db")
    cursor = conn.cursor()

    # Delete the row with the specified user_id
    cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))

    conn.commit()
    conn.close()
def confirmation(user_id):
    conn = sqlite3.connect("local.db")
    cursor = conn.cursor()

    # Check if the row with the specified user_id exists
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()

    if row is None:
        # Row with the specified user_id does not exist
        return False

    conn.commit()
    conn.close()
    # Check if all required fields are not empty
    return bool(row[0]) and bool(row[1]) and bool(row[2]) and bool(row[3]) and bool(row[4])
def photo_to_db(user_id, photo_data, photo_itself):  #Insert User ID and Photo:

    conn = sqlite3.connect("local.db")
    cursor = conn.cursor()

    # Insert user ID and photo into the database
    cursor.execute('''
        INSERT INTO users (user_id, photo_id, photo_itself) VALUES (?, ?, ?)
    ''', (user_id, photo_data, photo_itself))

    conn.commit()
    conn.close()
def location_to_db(user_id, latitude, longitude, time):    #Update User Location
    conn = sqlite3.connect("local.db")
    cursor = conn.cursor()

    # Update the user's location based on user ID

    cursor.execute('''
        UPDATE or REPLACE users SET latitude = ?, longitude = ?, timestamp = ? WHERE user_id = ?
    ''', (latitude, longitude, time, user_id))
    conn.commit()
    conn.close()
def get_photo(user_id):
    conn = sqlite3.connect("local.db")
    cursor = conn.cursor()

    # Fetch the photo for the specified user_id

    cursor.execute('SELECT photo_id FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()

    if row is not None:
            photo_id = row[0]
            return photo_id

    conn.commit()
    conn.close()
def get_location(user_id):
    conn = sqlite3.connect("local.db")
    cursor = conn.cursor()

    # Fetch the photo for the specified user_id
    cursor.execute('SELECT latitude FROM users WHERE user_id = ?', (user_id,))
    row1 = cursor.fetchone()

    row2 = cursor.execute('SELECT longitude FROM users WHERE user_id = ?', (user_id,))
    row2 = cursor.fetchone()

    if row1 and row2 is not None:
        latitude = row1[0]
        longitude = row2[0]
        return latitude, longitude

'''bigger.db'''

def change_status(status, photo_id, photo=True):
    if photo is True:
        conn = sqlite3.connect("bigger.db")
        cursor = conn.cursor()

        # Update the user's location based on user ID

        cursor.execute('''
            UPDATE or REPLACE reports SET status = ? WHERE photo_id = ?
        ''', (status, photo_id))


        conn.commit()
        conn.close()
    elif photo is False:
        conn = sqlite3.connect("bigger.db")
        cursor = conn.cursor()


        # Update the user's location based on user ID

        cursor.execute('''
                    UPDATE or REPLACE reports SET status = ? WHERE timestamp = ?
                ''', (status, photo_id))
        conn.commit()
        conn.close()
def init_big():
    conn_big_db = sqlite3.connect("bigger.db")
    cursor = conn_big_db.cursor()

    cursor.execute('''
           CREATE TABLE IF NOT EXISTS reports (
               user_id INTEGER,
               photo_id TEXT,
               photo_itself BLOB,
               latitude REAL,
               longitude REAL,
               status TEXT,
               timestamp DATETIME
           )
       ''')

    conn_big_db.commit()
    conn_big_db.close()
def upload_to_cloud(user_id):
    conn1 = sqlite3.connect("local.db")
    cursor = conn1.cursor()

    # Check if the row with the specified user_id exists
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn1.commit()
    conn1.close()

    conn = sqlite3.connect("bigger.db")
    cursor = conn.cursor()

    cursor.execute('''
            INSERT INTO reports (user_id, photo_id, photo_itself, latitude, longitude, status, timestamp) VALUES (?, ?, ?, ?, ?, 'Unvalidated', ?)
        ''', (row[0], row[1], row[2], row[3], row[4], row[5]))
    conn.commit()
    conn.close()
    delete_from_db(user_id)
    #TODO написати код для завантаження на хмару

init_local()
init_big()

