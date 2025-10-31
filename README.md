Of course. Here is the entire guide in simple, plain text that you can copy and paste without any formatting issues.

Getting Started: A Simple Text Guide

Part 1: Configuration (Do This First!)

You must edit three files to make sure everything can connect.

First, edit the backend files for the database connection.
Open the file named backend/app.py.
Find the section for mysql.connector.connect.
Change the host, user, and password to match your database.
Do the same thing for the file named backend/format.py.

Second, edit the Prometheus configuration.
Open the file named monitoring/prometheus.yml .
Make sure the targets are correct. For a local setup, 'localhost:8000' for the app and 'localhost:8002' for the script should be correct.

Part 2: Installation

You will need two separate terminals for this part.

For the Backend (Terminal 1):
First, navigate to the backend folder by typing:
cd C:\Users\zaidk\Desktop\mlops-main\backend
Next, create a virtual environment by typing:
python -m venv venv
Now, activate the environment by typing:
venv\Scripts\activate
Finally, install the required packages by typing:
pip install -r requirements.txt

For the Frontend (Terminal 2):
First, navigate to the frontend folder by typing:
cd C:\Users\zaidk\Desktop\mlops-main\frontend
Next, install the dependencies by typing:
npm install

Part 3: Running the Full Application

You need to open and run commands in several new terminals. The order is important. Keep each terminal open.

Terminal 1: Start Prometheus
First, navigate to your Prometheus folder by typing:
cd C:\Users\zaidk\Downloads\prometheus-3.7.3.windows-amd64\prometheus-3.7.3.windows-amd64
Next, run the Prometheus server by typing:
.\prometheus.exe --config.file=C:\Users\zaidk\Desktop\mlops-main\monitoring\prometheus.yml
Keep this terminal open.

Terminal 2: Start the MLflow Server
First, navigate to your main project folder by typing:
cd C:\Users\zaidk\Desktop\mlops-main
Next, start the MLflow server by typing:
mlflow ui
Keep this terminal open.

Terminal 3: Start the Backend API
First, navigate to the backend folder by typing:
cd C:\Users\zaidk\Desktop\mlops-main\backend
Next, activate the virtual environment by typing:
venv\Scripts\activate
Now, start the API server by typing:
uvicorn app:app --reload --port 8000
Keep this terminal open.

Terminal 4: Start the Frontend
First, navigate to the frontend folder by typing:
cd C:\Users\zaidk\Desktop\mlops-main\frontend
Next, start the frontend application by typing:
npm start
Keep this terminal open.

Part 4: How to Run the Data Script

You only need to do this when you want to load new data into the database.

First, open a new terminal.
Navigate to the backend folder by typing:
cd C:\Users\zaidk\Desktop\mlops-main\backend
Activate the virtual environment by typing:
venv\Scripts\activate
Finally, run the script by typing:
python format.py
This script will run and then finish.
