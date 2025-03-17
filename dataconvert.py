import sqlite3
import csv

def export_to_csv(db_path, table_name, output_path):
    conn = sqlite3.connect(db_path)  
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")  

    with open(output_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        # Write the header row (column names)
        writer.writerow([description[0] for description in cursor.description])
        # Write the rows of data
        writer.writerows(cursor.fetchall())

    conn.close()


export_to_csv('dataforairquality.db', 'air_metrics', 'data.csv')

