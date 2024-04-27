import csv
import pickle
import numpy as np
from flask import Flask, request, render_template, redirect, session, url_for

app = Flask(__name__)
app.secret_key = "super_secret_key"  # Secret key for session management
model = pickle.load(open('model.pkl', 'rb'))

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "adminpassword"


def is_admin_authenticated():
    return session.get('admin_logged_in', False)


def authenticate_admin(username, password):
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD


def add_record_to_csv(record):
    with open('Crop_recommendation.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(record)



@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if authenticate_admin(username, password):
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return render_template('login.html', error="Invalid credentials. Please try again.")
    return render_template('login.html')


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not is_admin_authenticated():
        return redirect(url_for('login'))
    if request.method == 'POST':
        # Extracting data from the form
        new_record = [
            request.form['N'],
            request.form['P'],
            request.form['K'],
            request.form['temperature'],
            request.form['humidity'],
            request.form['ph'],
            request.form['rainfall'],
            request.form['label']
        ]
        # Adding the new record to the CSV file
        add_record_to_csv(new_record)
        return "Record added successfully."
    return render_template('admin.html')


@app.route('/predict', methods=['POST'])
def predict():
    int_features = [int(x) for x in request.form.values()]
    final_features = [np.array(int_features)]
    prediction = model.predict(final_features)
    output = prediction
    return render_template('index.html',
                           prediction_text='Suggested crop for given  condition is: "{}".'.format(output[0]))


if __name__ == "__main__":
    app.run(debug=True)
