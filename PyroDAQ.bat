@echo off
title PyroDAQ

rem Activate the virtual environment
call PyroDAQvenv\Scripts\activate

rem Run the PyroDAQ application
python main.py
