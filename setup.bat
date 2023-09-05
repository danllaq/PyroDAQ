@echo off
title PyroDAQ

rem Creates virtual environment
echo Creating the virtual environment...
python -m venv PyroDAQvenv

rem Activates the virtual environment
echo Activating the virtual environment...
call PyroDAQvenv\Scripts\activate

rem Installs dependencies
echo Installing the required dependencies...
pip install -r requirements.txt

rem Display message to confirm that the script has completed
echo Setup completed!
