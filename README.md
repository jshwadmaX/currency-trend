💱 Real-Time Currency Trend Management System

A Flask-based web application for tracking, analyzing, and converting real-time currency exchange trends. The system provides secure authentication, live exchange rate analytics, and an intuitive dashboard for users.

🔗 Live Demo: https://currency-trend.onrender.com

🚀 Features

🔐 User Authentication (Signup, Login, Logout)

📊 Interactive Dashboard with Currency Statistics

💱 Real-Time Exchange Rate Tracking

🔁 Currency Conversion with History

👤 User Profile Management (Edit Profile)

🌐 RESTful API Endpoints

📱 Responsive UI using Bootstrap

🛠 Tech Stack

Backend

Python

Flask

REST APIs

Frontend

HTML5

CSS3

Bootstrap

JavaScript

Database

In-memory data storage (for demo & deployment simplicity)

Deployment

Render (Cloud Hosting)

🧩 Project Structure
currency-trend/
│
├── app.py
├── requirements.txt
├── templates/
│   ├── login.html
│   ├── signup.html
│   ├── dashboard.html
│   ├── profile.html
│   ├── edit_profile.html
│   ├── exchange_rates.html
│   └── currency_converter.html
│
├── static/
│   └── css/
└── README.md

⚙️ Installation & Setup
1️⃣ Clone the Repository
git clone https://github.com/your-username/currency-trend.git
cd currency-trend

2️⃣ Create Virtual Environment
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Run the Application
python app.py


App runs at:

http://127.0.0.1:3000

🔐 Authentication Flow

Passwords are securely hashed using SHA-256

Session-based authentication using Flask sessions

Protected routes using custom decorators

🧪 Sample Credentials
Username: demo
Password: demo123


(Or create a new account via signup)

📌 Future Enhancements

🔄 Persistent database integration (PostgreSQL / MySQL)

📈 Real-time exchange rate APIs (Forex / OpenExchangeRates)

🔔 Alerts for currency fluctuations

📊 Advanced analytics & visualization

🔐 OAuth-based authentication

👨‍💻 Author
jshwadmaX
