---

 Web Scanning Tools

A Python-based web scanning tool for performing Nmap and Nikto scans, managing scanning history, and generating reports.

---

 Prerequisites

Before running the application, ensure your system meets the following requirements:

- Python 3.8 or higher
- Linux/Unix-based system (Windows and macOS are also supported)
- Root/Administrator privileges (for installing dependencies)
- Internet connection (for downloading dependencies)
- MySQL server (for storing user accounts and scan results)

---

 Installation

 On Linux (Ubuntu)

bash
 1. Clone the repository
git clone https://github.com/Marcus0910/FYP.git

 2. Navigate to the project directory

cd FYP

 3. Update APT and install Python and pip

sudo apt update
sudo apt install python3 python3-pip

 4. Install dependencies and set up the environment

python3 setup.py

 5. Run the main program

python3 main.py


---

 On CentOS

bash
 1. Clone the repository

git clone https://github.com/Marcus0910/FYP.git

 2. Navigate to the project directory

cd FYP

 3. Install Python and pip (if not already installed)

sudo yum install python3 python3-pip

 4. Install dependencies and set up the environment

python3 setup.py

 5. Run the main program

python3 main.py


---

 On macOS

bash
 1. Clone the repository

git clone https://github.com/Marcus0910/FYP.git

 2. Navigate to the project directory

cd FYP

 3. Install Python and pip (if not already installed)
 macOS comes with Python pre-installed, but ensure pip is available

python3 -m ensurepip --upgrade

 4. Install dependencies and set up the environment

python3 setup.py

 5. Run the main program

python3 main.py


---

 Usage

1. Launch the application:
   Run the main.py script to start the application:
   bash
   python3 main.py
   

2. Create a new account:
   - When prompted, enter a username and password to register a new account.
   - Ensure the password meets the requirements (letters and numbers only).

3. Log in:
   - After registering, log in with your credentials.

4. Perform a scan:
   - Enter the target URL or IP address in the "Target" field.
   - Optionally, specify ports (e.g., 22,80,443).
   - Click Scan Ports to start the scan.

5. View and manage history:
   - All scan results are saved in the database.
   - Use the History tab to view, delete, or compare scan results.

6. Generate reports:
   - After a scan, click Generate Report to save the results as an HTML file.

---

 Configuration

The application uses a MySQL database for storing user accounts and scan results. The database configuration is defined in config.py:

python
DATABASECONFIG = {
    'user': 'root',
    'password': 'mysqlYRARJz',
    'host': '157.173.126.210',   MySQL server IP address
    'database': 'pythonfyp',
    'port': 3306,
}


 Steps to Configure MySQL Database

1. Set up MySQL server:
   - Install MySQL server if not already installed:
     bash
     sudo apt-get install mysql-server   For Ubuntu/Debian
     sudo yum install mysql-server       For CentOS
     
   - Start the MySQL service:
     bash
     sudo systemctl start mysql
     sudo systemctl enable mysql
     

2. Create the database:
   - Log in to MySQL:
     bash
     mysql -u root -p
     
   - Create a database:
     sql
     CREATE DATABASE pythonfyp;
     

3. Modify config.py:
   - Update the DATABASECONFIG with your MySQL server details.

---

 Safety Guidelines

- Only scan websites you have permission to test.
- Use the tool responsibly and in compliance with applicable laws and regulations.
- Keep your credentials secure.
- Regularly update the tool to the latest version.

---

 Common Issues

1. Installation fails:
   - Ensure your system meets the prerequisites.
   - Verify your internet connection.
   - Run the script with proper permissions (e.g., sudo on Linux).

2. Scan errors:
   - Check the target URL or IP address format.
   - Verify network connectivity and firewall settings.

3. Database connection issues:
   - Ensure the MySQL server is running and accessible.
   - Verify the database configuration in config.py.

---

 Support

For issues or questions, please refer to:
- Documentation: Requestment.txt
- GitHub Issues: https://github.com/Marcus0910/FYP/issues
- Email: 230152888@stu.vtc.edu.hk

---

 Version

Current Version: 1.0.0  
Last Updated: 5/2/2025

---

 About

A Python-based web scanning tool for performing Nmap and Nikto scans, managing scanning history, and generating reports.

---
