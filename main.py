"""Speedtest Logger

Description: Tests my ISP's speed and logs it to a SQLite database.
"""

# Imports
import subprocess
import speedtest as st
import sqlite3
from datetime import datetime


# Main
def main():
    # Check if mullvad vpn is on or off
    term_run = subprocess.run(
        'mullvad status', shell=True, capture_output=True)
    # Returns b'Disconnected' if vpn is off
    term_result = term_run.stdout.decode('utf-8')
    if term_result == "Disconnected\n":
        vpn_status = "OFF"
    else:
        vpn_status = "ON"

    # Connect to database
    db_file = "speedtest.db"
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Connected to {db_file}")
    except sqlite3.Error as e:
        print(e)

    # Current time
    now = datetime.now()
    # convert to human readable format
    now = now.strftime("%Y-%m-%d %H:%M:%S")

    # Create speedtest object
    speedtest = st.Speedtest()

    # Get server
    speedtest.get_best_server()

    # Get download speed
    download = speedtest.download()
    download = round(download / 1000000, 2)

    # Get upload speed
    upload = speedtest.upload()
    upload = round(upload / 1000000, 2)

    # Get ping
    ping = speedtest.results.ping
    ping = round(ping, 2)

    # Print results
    print(f"Current time: {now}")
    print(f"VPN Status: {vpn_status}")
    print(f"Download: {download}")
    print(f"Upload: {upload}")
    print(f"Ping: {ping}")

    # Check if table exists, else create it
    sql_table = """CREATE TABLE IF NOT EXISTS speedtest (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                vpn_status TEXT NOT NULL,
                download REAL NOT NULL,
                upload REAL NOT NULL,
                ping REAL NOT NULL
            );"""
    cur = conn.cursor()
    cur.execute(sql_table)
    conn.commit()

    # Insert results into database
    sql = """INSERT INTO speedtest (date, vpn_status, download, upload, ping)
                VALUES (?, ?, ?, ?, ?)"""
    cur = conn.cursor()
    cur.execute(sql, (now, vpn_status, download, upload, ping))
    conn.commit()
    print("Results inserted into database")

    # Close connection
    conn.close()
    print("Connection closed")


# Run main
if __name__ == "__main__":
    main()
