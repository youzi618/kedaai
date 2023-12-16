@echo off
set FLASK_APP=your_flask_app.py
set FLASK_ENV=production
waitress-serve --port=5000 your_flask_app:app
