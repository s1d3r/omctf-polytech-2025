import mysql.connector
from datetime import timedelta
import bcrypt
from random import randint

def hash_password(password: str) -> str:

    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def normalize_time_string(value):
    if not value:
        return None
    
    value = str(value)

    parts = value.split(":")
    if len(parts) == 3: 
        return f"{parts[0].zfill(2)}:{parts[1].zfill(2)}"
    if len(parts) == 2: 
        return f"{parts[0].zfill(2)}:{parts[1].zfill(2)}"

    return None


def get_connection():
    try:
        return mysql.connector.connect(
        host="mariadb",
        user="root",
        password="rootpassword",
        database="event_todo",
        autocommit=True
        )
    except Exception as err:
        print("Error: ", err)



def get_user(username):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()


        return user

    except Exception as err:
        print("Error: ", err)


def add_user(username, email, first_name, second_name, password):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        avatar_number = randint(1,12)

        avatar = f'/static/images/avatars/{25}.gif'

        password = hash_password(password)
        sql = """
            INSERT INTO users (username, email, first_name, second_name, avatar, password, role, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, 'user', NOW())
        """

        cursor.execute(sql, (username, email, first_name, second_name, avatar, password))
        cursor.execute("SELECT id, username, email, role FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        conn.commit()
        cursor.close()
        conn.close()
        
        return user
    except Exception as err:
        print("Error: ", err)


def update_user(user_id, params):
    try:

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        set_clause = ", ".join([f"{key} = %s" for key in params.keys()])
        sql = f"UPDATE users SET {set_clause} WHERE id = %s"
        values = list(params.values()) + [user_id]

        cursor.execute(sql, values)
        

        cursor.execute("SELECT id, username, role FROM users WHERE id=%s", (user_id,))
        user = cursor.fetchone()  
        conn.commit()
        cursor.close()
        conn.close()

        return user
    except Exception as err:
        print("Error: ", err)


def get_event(event_id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT e.id, e.title, e.status, e.date, e.time, e.location_address, e.owner_id, e.description, u.username AS owner_username
            FROM events e
            JOIN users u ON e.owner_id = u.id
            WHERE e.id = %s
        """, (event_id,))
        event = cursor.fetchone()

        if not event:
            cursor.close()
            conn.close()
            return None


        for key, val in event.items():
            if key == "time":
                event[key] = normalize_time_string(val)


        cursor.execute("""
            SELECT u.username
            FROM event_orgs eo
            JOIN users u ON eo.user_id = u.id
            WHERE eo.event_id = %s
        """, (event_id,))
        orgs = cursor.fetchall()
        event['organizers'] = [o['username'] for o in orgs]

        cursor.close()
        conn.close()
        return event

    except Exception as err:
        print("Error: ", err)


def add_event(title, user_id, invitecode, date, time, description):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            INSERT INTO events (title, owner_id, invitecode, date, time, description) VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (title, user_id, invitecode, date, time, description ))

        conn.commit()

        event_id = cursor.lastrowid

        cursor.close()
        conn.close()
        return event_id, 200
    except Exception as err:
        print("Error: ", err)
        if "Incorrect date value" in str(err):
            
            return "Incorrect value!", 400

        return err, 400


def update_event(event_id, params):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        if 'time' in params:
            if not params['time']:  
                params['time'] = None
            else:
                params['time'] = normalize_time_string(params['time'])
        

        set_clause = ", ".join([f"{key} = %s" for key in params.keys()])
        sql = f"UPDATE events SET {set_clause} WHERE id = %s"
        values = list(params.values()) + [event_id]

        cursor.execute(sql, values)
        
        conn.commit()
        cursor.close()
        conn.close()

        return 200
    except Exception as err:
        print("Error: ", err)
        return 400


def get_events():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT e.id, e.title, e.status, e.date, e.time, e.location_address, e.owner_id, e.description, u.username AS owner_username
            FROM events e
            JOIN users u ON e.owner_id = u.id
        """
        cursor.execute(query)
        events = cursor.fetchall()

        cursor.close()
        conn.close()

        for event in events:
            for key, val in event.items():
                if key == "time":
                    event[key] = normalize_time_string(val)

        return events

    except Exception as err:
        print("Error: ", err)

def add_event_org(invitecode, user_id, event_id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)


        cursor.execute("SELECT invitecode FROM events WHERE id = %s", (event_id, ))
        event_invitecode = cursor.fetchone()['invitecode']

        if event_invitecode == None:
            return 404

        if invitecode == event_invitecode:
            query = """
                INSERT INTO event_orgs (event_id, user_id) VALUES (%s, %s)
            """

            cursor.execute(query, (event_id, user_id))
            
            conn.commit()
            cursor.close()
            conn.close()

            return 200
        return 409


    except Exception as err:
        print("Error: ", err)
        return 400

def get_event_orgs(event_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            SELECT u.id
            FROM event_orgs eo
            JOIN users u ON u.id = eo.user_id
            WHERE eo.event_id = %s
        """

        cursor.execute(sql, (event_id,))
        result = cursor.fetchall()

        cursor.close()
        conn.close()

        return result

    except Exception as err:
        print("Error: ", err)

def get_event_tasks(event_id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM event_tasks WHERE event_id = %s", (event_id,))
        result = cursor.fetchall()

        cursor.close()
        conn.close()

        return result
    except Exception as err:
        print("Error: ", err)


def get_task(task_id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        sql = """
            SELECT * FROM event_tasks WHERE id=%s
        """

        cursor.execute(sql, (task_id, ))

        task = cursor.fetchone()

        cursor.close()
        conn.close()

        return task
    except Exception as err:
        print("Error: ", err)


def add_task(event_id, text, assigned_to, priority, deadline):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            INSERT INTO event_tasks (event_id, text, completed, assigned_to, priority, deadline)
            VALUES (%s, %s, FALSE, %s, %s, %s)
        """

        cursor.execute(sql, (event_id, text, assigned_to, priority, deadline))
        conn.commit()

        cursor.close()
        conn.close()
    except Exception as err:
        return {}, 400
        print("Error: ", err)


def update_task(id, value):
    try:

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)


        sql = "UPDATE event_tasks SET completed=%s WHERE id=%s"
        cursor.execute(sql, (value, id))
        
        conn.commit()
        cursor.close()
        conn.close()

        return 200
    except Exception as err:
        
        print("Error: ", err)
        return 400


def get_history(event_id, limit=20):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            f"SELECT * FROM event_history WHERE event_id = %s ORDER BY timestamp DESC LIMIT {int(limit)}",
            (event_id,)
        )
        result = cursor.fetchall()

        cursor.close()
        conn.close()

        return result
    except Exception as err:
        print("Error: ", err)
        return 400
