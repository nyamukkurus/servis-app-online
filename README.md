ServisApp

A simple web-based service management system built with Flask and MySQL, designed to track repair/service requests including customer data, device info, complaints, status, and payment details.

Features

Add, update, and delete service records via API or web interface

Search and filter services by keyword, type, or status

Automatic calculation of remaining payment (sisa)

JSON API endpoints for integration with frontend or other apps

MySQL database support (tested with PythonAnywhere MySQL)

Tech Stack

Backend: Python 3.x, Flask

Database: MySQL

Frontend: HTML, CSS, JavaScript

Deployment: PythonAnywhere (or any Flask hosting platform)
Setup

Clone the repository:

git clone https://github.com/nyamukkurus/servis-app-online.git
cd servisapp


Install dependencies:

pip install -r requirements.txt


Create a .env file with your MySQL credentials:

DB_HOST=your_mysql_host
DB_USER=your_mysql_user
DB_PASS=your_mysql_password
DB_NAME=your_database_name
DB_PORT=3306
FLASK_DEBUG=1


Run the app locally:

python app.py


Access in browser: http://127.0.0.1:5000/

API Endpoints

GET /api/servis → List all service records

POST /api/servis → Add a new service record

PUT /api/servis/<id> → Update a service record

DELETE /api/servis/<id> → Delete a service record

Notes

Remember to reload the app if using a hosting service like PythonAnywhere after changes.

Make sure your database user has proper permissions to create tables and read/write data.
