import mysql.connector
import datetime

class DataManager:
    def __init__(self, host="localhost", user="mofawij_user", password="0980", database="mofawij_db"):
        
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.conn.cursor()

        # Create table if not exists
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS crowd_log (
                id INT AUTO_INCREMENT PRIMARY KEY,
                timestamp DATETIME,
                people_count INT,
                congestion_level VARCHAR(50),
                gate_zone VARCHAR(50),
                density FLOAT,
                alert_triggered VARCHAR(50),
                gate_status VARCHAR(50),
                people_below_line INT
            )
        ''')
        self.conn.commit()

    def log_data(self, people_count, congestion_level, gate_zone, density, alert_triggered, gate_status, people_below_line):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        query = '''
            INSERT INTO crowd_log (timestamp, people_count, congestion_level, gate_zone, density, alert_triggered, gate_status, people_below_line)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        '''
        values = (timestamp, people_count, congestion_level, gate_zone, density, alert_triggered, gate_status, people_below_line)

        self.cursor.execute(query, values)
        self.conn.commit()

    def close(self):
        self.conn.close()