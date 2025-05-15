import sqlite3
import csv

file_path = "Call Center Data.csv"

conn = sqlite3.connect("call_center.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS CALL_CENTER (
    Id INTEGER PRIMARY KEY,
    IncomingCalls INTEGER,
    AnsweredCalls INTEGER,
    AnswerRate TEXT,
    AbandonedCalls INTEGER,
    AnswerSpeedAVG TEXT,
    TalkDurationAVG TEXT,
    WaitingTimeAVG TEXT,
    ServiceLevel20Sec TEXT
)
""")

with open(file_path, 'r', newline='') as file:
    reader = csv.DictReader(file)
    for row in reader:
        cursor.execute("""
            INSERT INTO CALL_CENTER (
                Id, IncomingCalls, AnsweredCalls, AnswerRate, AbandonedCalls,
                AnswerSpeedAVG, TalkDurationAVG, WaitingTimeAVG, ServiceLevel20Sec
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            int(row['Index']),
            int(row['Incoming Calls']),
            int(row['Answered Calls']),
            row['Answer Rate'],
            int(row['Abandoned Calls']),
            row['Answer Speed (AVG)'],
            row['Talk Duration (AVG)'],
            row['Waiting Time (AVG)'],
            row['Service Level (20 Seconds)']
        ))

print("Inserted Call Center Records:")
for row in cursor.execute("SELECT * FROM CALL_CENTER"):
    print(row)

conn.commit()
conn.close()
