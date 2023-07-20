# importing Flask and other modules
from flask import Flask, request, render_template, send_file, abort, session
from flask_cors import CORS
from io import BytesIO
import sqlite3
import qrcode
import time

# Flask constructor
app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path = '/static')
CORS(app)

app.secret_key = 'my-super-secret-key'
# Number of requests allowed per minute per IP address
REQUEST_LIMIT = 10

# Time period in seconds for which requests are counted
TIME_PERIOD = 120


@app.before_request
def block_user_agent():
    user_agent = request.headers.get("User-Agent")
    ip_address = request.remote_addr
    current_time = int(time.time())
    print(user_agent)
    print(ip_address)
    
    # Get the time of the last request from the session object
    last_request_time = session.get(ip_address, 0)

    # If the time of the last request is within the time period, increment the request count
    if last_request_time is not None and current_time - last_request_time < TIME_PERIOD:
        request_count = session.get(ip_address + user_agent, 0) + 1
    else:
        request_count = 1

    # Store the time of the last request and the request count in the session object
    session[ip_address] = current_time
    session[ip_address + user_agent] = request_count

    # If the request count exceeds the limit, abort the request with a 403 Forbidden error
    if request_count > REQUEST_LIMIT:
        abort(403)

# A decorator used to tell the application
# which URL is associated function
@app.route("/", methods =["GET", "POST"])
def index():
    return render_template('test.html')

@app.route('/Qrcode_Maker', methods =["GET", "POST"])

def gfg():
    if request.method == "POST":
        buffer = BytesIO()
       # getting input with name = fname in HTML form
        full_name = request.form.get("qrcode")
       # getting input with name = mname in HTML form
        group_number = request.form.get("qrcode2")
        # getting input with name = zname in HTML form
        last_name = request.form.get("qrcode1")
        # Create Tabel
        conn = sqlite3.connect('data.db')
        table_create_query = '''CREATE TABLE IF NOT EXISTS Student_Data (firstname TEXT, last_name TEXT, group_number INT, status TEXT)'''
        conn.execute(table_create_query)

        # Insert Data into the Database
        data_insert_query = ''' INSERT INTO Student_Data (firstname, last_name, group_number) VALUES (?, ?, ?) '''
        data_insert_tuple = (full_name, last_name, group_number)
        cursor = conn.cursor()
        cursor.execute(data_insert_query, data_insert_tuple)
        conn.commit()
        conn.close()
        # Create and save the Qrcode
        data = str(full_name)
        img = qrcode.make(data)
        img.save(buffer)
        img.save('static/Qrcode/'+str(full_name) +'.png')
        buffer.seek(0)
        response = send_file(buffer, mimetype='image/png')
        return response



    return render_template("Webpage.html")



@app.errorhandler(404)
def not_found_error(error):
    return render_template('notFound.html'), 404


if __name__=='__main__':
    app.run(debug = True, host='0.0.0.0', port='8080' )