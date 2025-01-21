import customtkinter as ctk
import subprocess
import sys
import threading
import os


# List of required Python packages
required_packages = [
    "customtkinter",
    "mysql-connector-python",
    "bcrypt"
]


# Function to install a package
def install_package(package, text_widget):
    try:
        text_widget.insert("end", f"Installing {package}...\n")
        text_widget.update()
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", package, "--quiet"])
        text_widget.insert("end", f"{package} installed successfully!\n")
        text_widget.update()
    except subprocess.CalledProcessError as e:
        text_widget.insert("end", f"Error installing {package}: {e}\n")
        text_widget.update()


# Function to change permissions of the "scripts" file
def change_permissions(file_path, text_widget, sudo_password):
    try:
        if os.path.exists(file_path):
            text_widget.insert("end", f"Changing permissions for {file_path}...\n")
            text_widget.update()
            # Run chmod with sudo
            command = f"echo {sudo_password} | sudo -S chmod 777 {file_path}"
            subprocess.run(command, shell=True, check=True)
            text_widget.insert("end", f"Permissions changed successfully for {file_path}.\n")
            text_widget.update()
        else:
            text_widget.insert("end", f"File {file_path} does not exist.\n")
            text_widget.update()
    except Exception as e:
        text_widget.insert("end", f"Error changing permissions: {e}\n")
        text_widget.update()


# Function to check and install dependencies
def install_dependencies(text_widget, button, sudo_password):
    # Disable the button to prevent multiple clicks
    button.configure(state="disabled")
    text_widget.insert("end", "Starting dependency installation...\n")
    text_widget.update()

    for package in required_packages:
        try:
            # Try importing the package to check if it's already installed
            __import__(package.split("-")[0])  # Split in case of dash-separated names
            text_widget.insert("end", f"{package} is already installed.\n")
            text_widget.update()
        except ImportError:
            # If the package is not installed, install it
            install_package(package, text_widget)

    # After installing dependencies, change permissions for "scripts"
    change_permissions("/usr/share/nmap/scripts", text_widget, sudo_password)

    text_widget.insert("end", "All dependencies are installed. You're ready to go!\n")
    text_widget.update()
    # Re-enable the button after installation is complete
    button.configure(state="normal")


# Function to start the installation in a separate thread
def start_installation_thread(text_widget, button, password_entry, agreement_checkbox):
    # Check if the user agreed
    if not agreement_checkbox.get():
        text_widget.insert("end", "You must agree to the terms to proceed.\n")
        text_widget.update()
        return

    sudo_password = password_entry.get()  # Get the sudo password from the entry box
    threading.Thread(target=install_dependencies, args=(
        text_widget, button, sudo_password)).start()


# Main UI setup
def main():
    # Initialize customtkinter
    ctk.set_appearance_mode("dark")  # Set theme to dark
    ctk.set_default_color_theme("blue")  # Set default color theme

    # Create the main window
    app = ctk.CTk()
    app.title("Dependency Installer")
    app.geometry("600x550")

    # Add a label
    label = ctk.CTkLabel(app, text="Dependency Installer", font=("Arial", 24))
    label.pack(pady=20)

    # Add a text box to display installation logs
    text_widget = ctk.CTkTextbox(app, width=550, height=200)
    text_widget.pack(pady=10)
    text_widget.insert(
        "end", "Welcome! Enter your sudo password and click the button below to install dependencies.\n")

    # Add a password entry box
    password_label = ctk.CTkLabel(app, text="Sudo Password:", font=("Arial", 14))
    password_label.pack(pady=5)
    password_entry = ctk.CTkEntry(app, show="*", width=300)  # Hide input with "*"
    password_entry.pack(pady=5)

    # Add an agreement checkbox
    agreement_checkbox = ctk.BooleanVar(value=False)  # Default checkbox state is unchecked
    agreement_label = ctk.CTkCheckBox(
        app,
        text="I agree to allow this tool to install dependencies and modify file permissions",
        variable=agreement_checkbox
    )
    agreement_label.pack(pady=10)

    # Add an install button
    install_button = ctk.CTkButton(
        app,
        text="Install Dependencies",
        command=lambda: start_installation_thread(
            text_widget, install_button, password_entry, agreement_checkbox)
    )
    install_button.pack(pady=20)

    # Run the main loop
    app.mainloop()


if __name__ == "__main__":
    main()
