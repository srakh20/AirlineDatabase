from flask import Flask, render_template, request
import psycopg2

app = Flask(__name__)

def get_db():
   return psycopg2.connect(
       dbname="p22",
       password="",
       host="localhost",
       port="5432"
   )


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/flights', methods=['POST'])
def flights():
    source = request.form['source']
    dest = request.form['destination']
    start_date = request.form['start_date']
    end_date = request.form['end_date']

    conn = get_db()
    cur = conn.cursor()

    query = """
    SELECT f.flight_number, f.departure_date, fs.origin_code, fs.dest_code, fs.departure_time
    FROM flight f
    JOIN flightService fs ON f.flight_number = fs.flight_number
    WHERE fs.origin_code = %s AND fs.dest_code = %s AND f.departure_date BETWEEN %s AND %s
    """

    cur.execute(query, (source, dest, start_date, end_date))
    flights = cur.fetchall()
    conn.close()

    return render_template('flights.html', flights=flights)


@app.route('/flight/<flight_number>/<departure_date>')
def flight_detail(flight_number, departure_date):

    conn = get_db()
    cur = conn.cursor()

    query = """
    SELECT a.capacity, COUNT(b.pid)
    FROM Flight f
    JOIN Aircraft a ON f.plane_type = a.plane_type
    LEFT JOIN Booking b
     ON f.flight_number = b.flight_number
    AND f.departure_date = b.departure_date
    WHERE f.flight_number = %s
     AND f.departure_date = %s
    GROUP BY a.capacity
    """

    query = """
    SELECT f.flight_number, f.departure_date, a.capacity, a.capacity-count(pid) as available_seats
    FROM flight f JOIN aircraft a ON f.plane_type=a.plane_type
    LEFT JOIN booking b ON f.flight_number=b.flight_number AND f.departure_date=b.departure_date
    WHERE f.flight_number = %s and f.departure_date=%s
    GROUP BY f.flight_number, f.departure_date, a.capacity;
    """

    cur.execute(query, (flight_number, departure_date))
    result = cur.fetchone()

    capacity = result[2]
    available = result[3]

    conn.close()

    return render_template(
        'flight_detail.html',
        flight_number=flight_number,
        date=departure_date,
        capacity=capacity,
        available=available
    )


if __name__ == '__main__':
    app.run(debug=True)
