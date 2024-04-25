import sqlite3

# Connect to the source database
source_conn = sqlite3.connect('unique_job_database.db')
source_cur = source_conn.cursor()

# Connect to the destination database
dest_conn = sqlite3.connect('unique_database.db')
dest_cur = dest_conn.cursor()

# Attach the source database to the destination database
dest_cur.execute("ATTACH DATABASE 'unique_job_database.db' AS source_db")

# Copy the unique_jobs table from the source database to the destination database
dest_cur.execute("CREATE TABLE IF NOT EXISTS unique_jobs AS SELECT * FROM source_db.unique_jobs")

# Commit the transaction and close connections
dest_conn.commit()
source_conn.close()
dest_conn.close()

print("Table 'unique_jobs' copied successfully from unique_job_database.db to new_database.db.")
