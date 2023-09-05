@echo off
title PyroDAQ

rem Creating virtual environment
python -m venv PyroDAQvenv

rem Activating the virtual environment
PyroDAQvenv\Scripts\activate

rem Installing dependencies
pip install -r requirements.txt
