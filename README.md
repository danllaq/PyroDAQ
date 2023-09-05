# PyroDAQ
Python app with GUI that interacts with National Instruments DAQ for temperature sensing

## Prerequisites
Before you begin, make sure you have Python and Pip installed on your system and that you're using Windows
### Installing Python
1. Visit the [Python Dowloads](https://www.python.org/downloads/) page
2. Download the installer for the version *3.11.0*
3. Run the installer and follow the installation instructions
4. During the installation, make sure to check the box that says "Add Python to PATH."
5. After installation, open a command prompt and check that Python is installed by running:
```batch
python -- version
```
### Installing Pip
When installing Python, pip should also be included. To check if it's installed run:
```batch 
pip --version
```
If for any reason there's a problem refer to [pip documentation](https://pip.pypa.io/en/stable/installation/)

## Setting up the project
### Downloading the project
1. From [project's page](https://github.com/danllaq/PyroDAQ) download zip file
2. Extract the zip file and save the project in your chosen directory
### Virtual Environment
In order to isolate dependencies for this project, we're going to create a virtual environment. It's important to note that
the project and dependencies are going to be inside the venv but *Python and pip **should not be** in the venv*

To quickly set up and configure this project, follow these steps:
1. Copy the path of your project's directory
1. Open a command prompt and open the directory
```bash
cd C:\Users\<user_name>\<folder>\PyroDAQ
```
3. Run the setup script:
```bash
setup.bat
```

### Installing the Required Driver
To use this project, you need to install the NI-DAQmx dirver, version 2023 Q1. Follow these steps to download and install the driver:
1. **Download the NI-DAQmx Driver:**
  - Visit the official NI-DAQmx driver download pager: [NI-DAQmx Driver Download](https://www.ni.com/es/support/downloads/drivers/download.ni-daq-mx.html#477807)
  - Choose Windows OS and the 2023 Q1 version
  - Click download button and save to computer
2. **Installation:**
  - Locate the .exe file and double-click
  - Follow the instructions
3. **Verification:**
  - Verify the installation by opening NI MAX
  - Open the "My System > Software"
  - You should see the driver and the correct version

