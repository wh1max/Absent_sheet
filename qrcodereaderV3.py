import cv2
import pyzbar.pyzbar as pyzbar
import sqlite3
import pdfkit
import pandas as pd

conn  = sqlite3.connect('data.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS attendance (id INTEGER PRIMARY KEY, qr_data TEXT, status TEXT)''')
conn.commit()

cursor.execute('SELECT qr_data FROM attendance')
authorized_data = set(row[0] for row in cursor.fetchall())

# Start the video capture
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

while True:
    # Capture the video frame
    success, frame = cap.read()
    
    # Export the data as an HTML file
    df=pd.read_sql_query('SELECT * FROM Student_Data', conn)
    df.to_html('static/data.html')
    
    # Decode the QR codes in the frame
    decoded_objs = pyzbar.decode(frame)

    for obj in decoded_objs:
        qr_data = obj.data.decode()

        # Check if the QR code data is in the authorized data
        if qr_data in authorized_data:
            status = 'Authorized'
            color = (0, 255, 0)
            attendance_status = 'Present'
        else:
            status = 'Unauthorized'
            color = (0, 0, 255)
            attendance_status = 'Absent'

        # Draw the border around the QR code
        (x, y, w, h) = obj.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

        # Write the QR code data and status on the frame
        cv2.putText(frame, status, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        cv2.putText(frame, qr_data, (x, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # Write the attendance status to the database
        cursor.execute("UPDATE attendance SET status = ? WHERE qr_data = ?", (attendance_status, qr_data))
        conn.commit()

    # Show the frame
    cv2.imshow('QR Code Scanner', frame)

    # Exit the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and close the window
cap.release()
cv2.destroyAllWindows()

# Close the database connection
conn.close()