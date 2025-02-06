import subprocess
import platform
import os
import sys

# List of required Python packages
REQUIRED_PACKAGES = [
    "mysql-connector-python",  # 從 login_page.py
    "bcrypt",                 # 從 login_page.py
    "customtkinter",          # 從多個文件使用
    "distro",                # 用於檢測 Linux 發行版
    "pyperclip",             # 從 settings_tab.py
    "xml",                   # 內建
    "tkinter",               # 內建，但需要系統包 python3-tk
    "threading",             # 內建
    "subprocess",            # 內建
    "os",                    # 內建
    "sys",                   # 內建
]

# List of required system packages
SYSTEM_PACKAGES = [
    "python3-tk",            # tkinter 的系統依賴
    "python3-pip",           # pip 安裝器
    "nmap",                  # nmap 掃描工具
    "nikto",                 # nikto 掃描工具
    "python3-dev",           # Python 開發包
    "default-libmysqlclient-dev"  # MySQL 客戶端開發包
]

# Detect the operating system
def detect_os():
    """Detect the operating system"""
    system = platform.system().lower()
    if system == "linux":
        try:
            import distro
            linux_distro = distro.id().lower()
        except ImportError:
            linux_distro = "unknown"
        return "linux", linux_distro
    return "unknown", ""
    
def install_pip():
    """Install pip if it's not already installed"""
    try:
        # 檢查 pip 是否已安裝
        subprocess.check_call([sys.executable, "-m", "pip", "--version"])
        print("pip is already installed")
    except subprocess.CalledProcessError:
        print("Installing pip...")
        try:
            # 使用 ensurepip 模組安裝 pip
            subprocess.check_call([sys.executable, "-m", "ensurepip", "--default-pip"])
            print("pip installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Error installing pip: {e}")
            print("Trying alternative method...")
            try:
                # 如果 ensurepip 失敗，嘗試使用 apt 安裝
                subprocess.check_call(["sudo", "apt-get", "install", "-y", "python3-pip"])
                print("pip installed successfully using apt!")
            except subprocess.CalledProcessError as e:
                print(f"Error installing pip using apt: {e}")
                return False
    return True

def install_system_package(package, root_password):
    """Install a system package using apt-get"""
    try:
        print(f"Installing system package {package}...")
        update_cmd = f"echo {root_password} | sudo -S apt-get update"
        install_cmd = f"echo {root_password} | sudo -S apt-get install -y {package}"
        
        # First update package list
        subprocess.run(update_cmd, shell=True, capture_output=True, text=True)
        
        # Then install the package
        result = subprocess.run(install_cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"{package} installed successfully!")
            return True
        else:
            print(f"Error installing {package}: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error installing {package}: {str(e)}")
        return False

# Install a Python package
def install_package(package):
    """Install a Python package using pip"""
    try:
        print(f"Installing {package}...")
        # 首先嘗試正常安裝
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package, "--quiet"],
            capture_output=True,
            text=True
        )
        
        # 檢查是否出現 externally-managed-environment 錯誤
        if "externally-managed-environment" in result.stderr:
            print(f"Detected externally managed environment, retrying with --break-system-packages...")
            # 使用 --break-system-packages 重試安裝
            subprocess.check_call([
                sys.executable, 
                "-m", 
                "pip", 
                "install", 
                package, 
                "--break-system-packages",
                "--quiet"
            ])
        elif result.returncode != 0:
            # 如果是其他錯誤，拋出異常
            raise subprocess.CalledProcessError(result.returncode, result.args, result.stdout, result.stderr)
            
        print(f"{package} installed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"Error installing {package}: {e}")
        try:
            # 如果 pip 安裝失敗，嘗試使用 apt 安裝
            subprocess.check_call(["sudo", "apt-get", "install", "-y", f"python3-{package}"])
            print(f"{package} installed successfully using apt!")
        except subprocess.CalledProcessError as e:
            print(f"Error installing {package} using apt: {e}")


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
        # 使用 which 命令來檢查工具是否安裝
        result = subprocess.run(['which', tool], capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"Error checking {tool}: {str(e)}")
        return False

def install_tools(os_type, linux_distro, root_password):
    if os_type == "LINUX":
        if linux_distro in ["UBUNTU", "DEBIAN", "KALI"]:
            # 對於 Ubuntu/Debian/Kali Linux
            commands = [
                "apt-get update",
                "apt-get install -y nmap",
                "apt-get install -y nikto"
            ]
        elif linux_distro == "centos":
            # 對於 CentOS
            commands = [
                "yum update -y",
                "yum install -y nmap",
                "yum install -y nikto"
            ]
        else:
            print(f"Unsupported Linux distribution: {linux_distro}")
            return

        # 執行命令
        for cmd in commands:
            try:
                full_cmd = f"echo {root_password} | sudo -S {cmd}"
                process = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
                if process.returncode == 0:
                    print(f"Successfully executed: {cmd}")
                else:
                    print(f"Failed to execute {cmd}")
                    print(f"Error: {process.stderr}")
            except Exception as e:
                print(f"Error executing command: {str(e)}")

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
    print("Warning: Some packages might require system-wide installation.")
    print("The script will use --break-system-packages if necessary.")
    print("=========================================================")

    if not install_pip():
        print("Failed to install pip. Some packages may not install correctly.")

        # First install system packages
    for package in SYSTEM_PACKAGES:
        install_system_package(package, root_password)
    
    print("\nInstalling Python packages...")
    # Then install Python packages
    for package in REQUIRED_PACKAGES:
        try:
            __import__(package.split("-")[0])
            print(f"{package} is already installed.")
        except ImportError:
            install_package(package)

    print("\nAll dependencies are installed. Ready to go!")

# Print a separator line
def print_separator():
    print("\n" + "=" * 50 + "\n")

# Main script
if __name__ == "__main__":
    os_type, linux_distro = detect_os()
    
    print_separator()
    print(f"Detected OS: {os_type.upper()}")
    if linux_distro:
        print(f"Linux Distribution: {linux_distro.upper()}")
    print_separator()
    
    root_password = input("Enter your system password (leave blank if not needed): ")
    print_separator()
    
    install_dependencies(root_password)
    print_separator()
