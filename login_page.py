import customtkinter as ctk
import re  # Import the regex library for email validation
from tkinter import messagebox
from tabbed_nmap_app import TabbedNmapApp  # Import the main app
import mysql.connector
from mysql.connector import errorcode
import bcrypt
from config import DATABASE_CONFIG  # Import database config


class LoginPage(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Login Page")
        self.geometry("500x400")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.active_frame = None
        self.show_login_frame()

    def show_login_frame(self):
        """Display the login screen."""
        if self.active_frame:
            self.active_frame.destroy()

        self.active_frame = ctk.CTkFrame(self)
        self.active_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(self.active_frame, text="Login", font=("Arial", 24, "bold")).pack(pady=10)

        ctk.CTkLabel(self.active_frame, text="Email (UserID):").pack(pady=5)
        self.userid_entry = ctk.CTkEntry(self.active_frame, width=250, placeholder_text="Enter your email")
        self.userid_entry.pack(pady=5)

        ctk.CTkLabel(self.active_frame, text="Password:").pack(pady=5)
        self.password_entry = ctk.CTkEntry(
            self.active_frame, width=250, placeholder_text="Enter your password", show="*"
        )
        self.password_entry.pack(pady=5)

        login_button = ctk.CTkButton(self.active_frame, text="Login", command=self.login)
        login_button.pack(pady=10)

        switch_to_signup = ctk.CTkButton(
            self.active_frame, text="Don't have an account? Sign Up", command=self.show_signup_frame
        )
        switch_to_signup.pack(pady=10)

    def show_signup_frame(self):
        """Display the signup screen."""
        if self.active_frame:
            self.active_frame.destroy()

        self.active_frame = ctk.CTkFrame(self)
        self.active_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(self.active_frame, text="Sign Up", font=("Arial", 24, "bold")).pack(pady=10)

        ctk.CTkLabel(self.active_frame, text="Email (UserID):").pack(pady=5)
        self.new_userid_entry = ctk.CTkEntry(self.active_frame, width=250, placeholder_text="Enter your email")
        self.new_userid_entry.pack(pady=5)

        ctk.CTkLabel(self.active_frame, text="Password:").pack(pady=5)
        self.new_password_entry = ctk.CTkEntry(
            self.active_frame, width=250, placeholder_text="Enter a password", show="*"
        )
        self.new_password_entry.pack(pady=5)

        ctk.CTkLabel(self.active_frame, text="Confirm Password:").pack(pady=5)
        self.confirm_password_entry = ctk.CTkEntry(
            self.active_frame, width=250, placeholder_text="Confirm your password", show="*"
        )
        self.confirm_password_entry.pack(pady=5)

        signup_button = ctk.CTkButton(self.active_frame, text="Sign Up", command=self.signup)
        signup_button.pack(pady=10)

        switch_to_login = ctk.CTkButton(
            self.active_frame, text="Already have an account? Login", command=self.show_login_frame
        )
        switch_to_login.pack(pady=10)

    def login(self):
        """Handle user login."""
        userid = self.userid_entry.get().strip()
        password = self.password_entry.get().strip()

        if not self.validate_email_format(userid):
            self.show_message("Error", "Please enter a valid email address.")
            return
        if not password:
            self.show_message("Error", "Please enter your password.")
            return

        try:
            db = mysql.connector.connect(**DATABASE_CONFIG)
            cursor = db.cursor()

            sql = "SELECT password FROM UserName WHERE UserID = %s"
            val = (userid,)
            cursor.execute(sql, val)
            result = cursor.fetchone()

            if result:
                hashed_password = result[0]
                try:
                    if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                        self.show_message("Success", "Login successful!", success=True)
                        self.open_main_page()
                    else:
                        self.show_message("Error", "Invalid email or password.")
                except ValueError as e:
                    self.show_message("Error", "Invalid password format. Please reset your password.")
            else:
                self.show_message("Error", "Invalid email or password.")

        except mysql.connector.Error as err:
            self.show_message("Error", f"Database error: {err}")
        finally:
            if cursor:
                cursor.close()
            if db.is_connected():
                db.close()

    def signup(self):
        """Handle user signup."""
        userid = self.new_userid_entry.get().strip()
        password = self.new_password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()

        if not self.validate_email_format(userid):
            self.show_message("Error", "Please enter a valid email address.")
            return
        if not password or not confirm_password:
            self.show_message("Error", "All fields are required.")
            return
        if password != confirm_password:
            self.show_message("Error", "Passwords do not match.")
            return

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        try:
            db = mysql.connector.connect(**DATABASE_CONFIG)
            cursor = db.cursor()

            sql = "INSERT INTO UserName (UserID, password) VALUES (%s, %s)"
            val = (userid, hashed_password)
            cursor.execute(sql, val)
            db.commit()

            self.show_message("Success", "Account created successfully! Please login.")
            self.show_login_frame()

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_DUP_ENTRY:
                self.show_message("Error", "Email already exists.")
            else:
                self.show_message("Error", f"Database error: {err}")
        finally:
            if cursor:
                cursor.close()
            if db.is_connected():
                db.close()

    def validate_email_format(self, email):
        """Validate email format using a regex."""
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email)

    def show_message(self, title, message, success=False):
        """Display a message box."""
        message_box = ctk.CTkToplevel(self)
        message_box.title(title)
        message_box.geometry("400x200")

        ctk.CTkLabel(message_box, text=message, font=("Arial", 14), wraplength=350).pack(pady=20, padx=20)
        ctk.CTkButton(message_box, text="OK", command=lambda: self.handle_message_box_close(message_box, success)).pack(pady=10)

    def handle_message_box_close(self, message_box, success):
        """Close the message box and proceed if successful."""
        message_box.destroy()
        if success:
            self.open_main_page()

    def open_main_page(self):
        """Open the main application."""
        self.destroy()
        root = ctk.CTk()
        app = TabbedNmapApp(root)
        root.mainloop()

    def on_close(self):
        """Close the application."""
        self.destroy()
