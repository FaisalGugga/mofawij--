import mysql.connector
import pandas as pd
from datetime import datetime
import os

def export_logs_to_excel(
    host="localhost", 
    user="mofawij_user", 
    password="0980", 
    database="mofawij_db", 
    table_name="crowd_log", 
):
    # Connect to the database
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        df_new = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    
        date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") 
        file_name = f"congestion_data_{date_str}.csv"
        
        if os.path.exists(file_name):
            df_existing = pd.read_excel(file_name)
            
            
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            
        else:
            df_combined = df_new
            
        df_combined.to_csv(file_name, index=False)
        print(f"Data exported to {file_name}")
            
    
    except Exception as e:
        print(e)
    finally:
        if conn.is_connected():
         conn.close()
         print("Connection closed.")
if __name__ == "__main__":
    export_logs_to_excel()
    