import subprocess
import platform
import os

# List of required Python packages
REQUIRED_PACKAGES = [
    "mysql-connector-python",
    "bcrypt",
    "distro",
    "customtkinter"
]

# Detect the operating system
def detect_os():
    system = platform.system().lower()
    if system == "linux":
        try:
            import distro
            linux_distro = distro.id().lower()
        except ImportError:
            linux_distro = "unknown"
        return "linux", linux_distro
    elif system == "darwin":
        return "macos", ""
    elif system == "windows":
        return "windows", ""
    else:
        return "unknown", ""

# Install a Python package
def install_package(package):
    try:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])
        print(f"{package} installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error installing {package}: {e}")

# Execute a system command and handle output
def run_command(command, root_password=None):
    try:
        if root_password:
            command = f"echo {root_password} | sudo -S {command}"
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        output, error = process.communicate()
        if process.returncode == 0:
            print(f"Command executed successfully: {command}")
        else:
            print(f"Command failed: {error.decode()}")
    except Exception as e:
        print(f"Error executing command: {str(e)}")

# Check if a tool is installed
def is_tool_installed(tool):
    try:
        subprocess.check_call([tool, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"{tool} is already installed.")
        return True
    except subprocess.CalledProcessError:
        print(f"{tool} is not installed.")
        return False

# Install nikto and nmap based on the operating system
def install_tools(os_type, linux_distro, root_password):
    if os_type == "linux":
        if linux_distro in ["ubuntu", "debian", "kali"]:
            # For Ubuntu, Debian, and Kali Linux
            commands = [
                "apt-get update",
                "apt-get install -y nmap nikto"
            ]
        elif linux_distro == "centos":
            # For CentOS
            commands = [
                "yum update -y",
                "yum install -y nmap nikto"
            ]
        else:
            print(f"Unsupported Linux distribution: {linux_distro}")
            return
    elif os_type == "windows":
        # For Windows
        commands = [
            "choco install nmap -y",
            "choco install nikto -y"
        ]
    elif os_type == "macos":
        # For macOS
        commands = [
            "brew install nmap nikto"
        ]
    else:
        print("Unsupported operating system")
        return

    # Execute commands
    for cmd in commands:
        run_command(cmd, root_password if os_type == "linux" else None)

# Check and install dependencies
def install_dependencies(root_password):
    print("Starting dependency installation...")

    # Check and install nikto and nmap
    if not is_tool_installed("nmap") or not is_tool_installed("nikto"):
        print("Installing nikto and nmap...")
        install_tools(os_type, linux_distro, root_password)

    # Install Python packages
    for package in REQUIRED_PACKAGES:
        try:
            __import__(package.split("-")[0])
            print(f"{package} is already installed.")
        except ImportError:
            install_package(package)

    print("All dependencies are installed. Ready to go!")

# Print a separator line
def print_separator():
    print("\n" + "=" * 50 + "\n")

# Main script
if __name__ == "__main__":
    # Show the user's OS
    os_type, linux_distro = detect_os()
    print_separator()
    print(f"Detected OS: {os_type.upper()}")
    if linux_distro:
        print(f"Linux Distribution: {linux_distro.upper()}")
    print_separator()

    # Install dependencies
    root_password = input("Enter your system password (leave blank if not needed): ")
    print_separator()
    install_dependencies(root_password)
    print_separator()
