# PyroDAQ 🐍🌡️
PyroDAQ is a Python application with a graphical user interface (GUI) designed for interacting with 
National Instruments DAQ (Data Acquisition) devices for temperature sensing. 🔥

## Prerequisites 📋

Before you begin, make sure you have Python and Pip installed on your system and that you're using Windows. 💻

### Python Installation 🐍
1. Visit the [Python Dowloads](https://www.python.org/downloads/) page.
2. Download the installer for the version *3.11.0*.
3. Run the installer and follow the installation instructions.
4. During the installation, make sure to check the box that says "Add Python to PATH".
5. After installation, open a command prompt and check that Python is installed by running:
```batch
python -- version
```

### Pip Installation 📦

When installing Python, pip should also be included. To check if it's installed run:
```batch 
pip --version
```
If for any reason there's a problem refer to [pip documentation](https://pip.pypa.io/en/stable/installation/).

### Driver Installation ⚙️

To use PyroDAQ, you need to install the NI-DAQmx (version 2023 Q1). 

Downloading and installing the NI-DAQmx driver is essential because it provides the necessary software components for your 
computer to communicate with and control National Instruments DAQ hardware devices that this project uses.

Follow these steps to download and install the driver:
1. **Download the NI-DAQmx Driver:**
  - Visit the official NI-DAQmx driver download pager: [NI-DAQmx Driver Download](https://www.ni.com/es/support/downloads/drivers/download.ni-daq-mx.html#477807).
  - Choose Windows OS and the 2023 Q1 version.
  - Click download button and save to computer.
2. **Installation:**
  - Locate the .exe file and double-click.
  - Follow the instructions.
3. **Verification:**
  - Verify the installation by opening NI MAX.
  - Open the "My System > Software".
  - You should see the driver and the correct version.

## Setting up the project 🛠️

### Downloading the project 📥
1. From [PyroDAQ GitHub page](https://github.com/danllaq/PyroDAQ) download zip file.
2. Extract the zip file to your prefered directory.
   
### Creating a virtual environment 🌐
In order to isolate dependencies for this project, we're going to create a virtual environment. It's important to note that
the project and dependencies are going to be inside the venv but *Python and pip **should not be** in the venv* ❗

To quickly set up and configure this project, follow these steps:
1. Copy the path of your project's directory.
1. Open a command prompt and open the directory with the following command (substituting for your actual path):
```bash
cd C:\Users\<user_name>\PyroDAQ-main
```
3. Run the setup script:
```bash
setup.bat
```
4. Wait until the setup has finished, it might take a few seconds.

## Running the Program ▶️

After you have completed the prerequisites and set up the project, follow these steps to run PyroDAQ:
1. **Launch PyroDAQ:**
   You have some options for running the program:
   - In a command line, from your project directory, run:
     ```bash
     PyarDAQ.bat
     ```
   - You can also double click on the file `PyroDAQ.bat`
   - Or in a command line your project directory, run:
     ```bash
     PyroDAQvenv\Scripts\activate
     python main.py
     ```
3. **Interact with the program**
    - Once the program is running, the GUI for PyroDAQ should appear
    - You can now connect you DAQ and use the GUI to interact with it for temperature sensing and other data tasks
4. **Student's Guide**
   - You can find more instructions and a guide through the program in the attached pdf "Student's Guide"

## That's It! You're Set to Blaze a Trail with PyroDAQ 🐍🌡️

Congratulations! You've successfully set up PyroDAQ and are now ready to embark on your data acquisition adventures. Whether you're a seasoned engineer, a curious hobbyist, or somewhere in between, we hope PyroDAQ adds some heat to your temperature sensing projects!

Remember, the world of data acquisition is vast and filled with exciting challenges. So, go forth, measure temperatures, and conquer your data like a pro. 

Happy data collecting, and stay toasty! 🔥😄


