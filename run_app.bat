@echo off
echo Starting Live Stock Monitor...
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting the web application...
echo Open your browser and go to: http://localhost:5000
echo.
python app.py
pause
