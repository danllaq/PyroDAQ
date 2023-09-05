@echo off
title PyroDAQ

rem Creating virtual environment
python -m venv PyroDAQvenv
echo Creating the virtual environment...

rem Activating the virtual environment
PyroDAQvenv\Scripts\activate
echo Activating the virtual environment...

rem Installing dependencies
pip install -r requirements.txt
echo Installing the required dependencies...

rem Display message to confirm that the script has completed
echo Setup completed!
