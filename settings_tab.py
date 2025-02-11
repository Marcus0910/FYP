import customtkinter as ctk
import webbrowser
import os
import pyperclip
import json
from tkinter import messagebox


class SettingsTab:
    def __init__(self, parent):
        self.parent = parent
        self.settings_file = "settings.json"  # Settings file path
        self.load_settings()  # Load settings
        self.build_settings_tab()

    def build_settings_tab(self):
        """Build settings tab interface"""
        main_frame = ctk.CTkFrame(self.parent, fg_color="#1A1A1A")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Left and right columns layout
        columns_frame = ctk.CTkFrame(main_frame, fg_color="#1A1A1A")
        columns_frame.pack(fill="both", expand=True)

        # Left column (Nmap Settings)
        left_column = ctk.CTkFrame(columns_frame, fg_color="#1A1A1A")
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Nmap Settings Title
        ctk.CTkLabel(left_column, text="Nmap Settings", font=('Arial', 16, 'bold'), 
                    text_color="#00FF00").pack(pady=10)

        # Default NSE Script Settings section
        default_frame = ctk.CTkFrame(left_column, fg_color="#1A1A1A")
        default_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(default_frame, text="Default NSE Script Settings", 
                    font=('Arial', 14, 'bold'), text_color="#00FF00").pack(pady=5)

        # Default NSE Script Options - Removed "Use Default Scripts"
        self.default_nse_var = ctk.StringVar(value=self.settings.get("default_nse_option", "all"))
        default_options = [
            ("Use All Scripts (/all)", "all"),
            ("Custom Scripts", "custom")
        ]

        for text, value in default_options:
            ctk.CTkRadioButton(
                default_frame,
                text=text,
                variable=self.default_nse_var,
                value=value,
                command=self.update_nse_input,
                fg_color="#00FF00",
                text_color="#00FF00"
            ).pack(pady=2, padx=20, anchor="w")

        # Custom NSE Script Input
        ctk.CTkLabel(left_column, text="Enter NSE Script Name:", text_color="#00FF00").pack(pady=5)
        self.nse_script_input = ctk.CTkEntry(left_column, 
                                           placeholder_text="Enter NSE script name")
        self.nse_script_input.pack(pady=5)
        
        # Update NSE input based on saved settings
        self.update_nse_input()

        # Open NSE Files Button
        nse_button = ctk.CTkButton(
            left_column,
            text="Open NSE Files",
            command=self.open_nse_files,
            fg_color="#333333",
            hover_color="#444444"
        )
        nse_button.pack(pady=5)

        # Timing Mode
        ctk.CTkLabel(left_column, text="Select Timing Mode (T1-T5):", 
                    text_color="#00FF00").pack(pady=5)
        self.timing_mode_var = ctk.StringVar(value=self.settings.get("timing_mode", "T1"))
        self.timing_mode_option = ctk.CTkOptionMenu(
            left_column,
            variable=self.timing_mode_var,
            values=["T1", "T2", "T3", "T4", "T5"],
            fg_color="#333333",
            button_color="#333333",
            button_hover_color="#444444"
        )
        self.timing_mode_option.pack(pady=5)

        # User-Agent Settings
        ctk.CTkLabel(left_column, text="User-Agent Settings", 
                    font=('Arial', 16, 'bold'), text_color="#00FF00").pack(pady=20)

        # Nmap User-Agent
        ctk.CTkLabel(left_column, text="Custom Nmap User-Agent:", 
                    text_color="#00FF00").pack(pady=5)
        self.nmap_user_agent = ctk.StringVar(value=self.settings.get("nmap_user_agent", "Chrome"))
        self.nmap_user_agent_option = ctk.CTkOptionMenu(
            left_column,
            variable=self.nmap_user_agent,
            values=["Chrome", "Firefox", "Brave", "Edge"],
            fg_color="#333333",
            button_color="#333333",
            button_hover_color="#444444"
        )
        self.nmap_user_agent_option.pack(pady=5)

        # Nikto User-Agent
        ctk.CTkLabel(left_column, text="Custom Nikto User-Agent:", 
                    text_color="#00FF00").pack(pady=5)
        self.nikto_user_agent = ctk.StringVar(value=self.settings.get("nikto_user_agent", "Chrome"))
        self.nikto_user_agent_option = ctk.CTkOptionMenu(
            left_column,
            variable=self.nikto_user_agent,
            values=["Chrome", "Firefox", "Brave", "Edge"],
            fg_color="#333333",
            button_color="#333333",
            button_hover_color="#444444"
        )
        self.nikto_user_agent_option.pack(pady=5)

        # Right column (Search functionality)
        right_column = ctk.CTkFrame(columns_frame, fg_color="#1A1A1A")
        right_column.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # Search NSE Scripts Title
        ctk.CTkLabel(right_column, text="Search NSE Scripts", 
                    font=('Arial', 16, 'bold'), text_color="#00FF00").pack(pady=10)

        # Search box
        self.search_entry = ctk.CTkEntry(right_column, placeholder_text="Enter keyword")
        self.search_entry.pack(pady=5)

        # Search button
        search_button = ctk.CTkButton(
            right_column,
            text="Search",
            command=self.search_nse_scripts,
            fg_color="#333333",
            hover_color="#444444"
        )
        search_button.pack(pady=5)

        # Search results display
        self.search_results = ctk.CTkTextbox(
            right_column, 
            height=300,  # Increased height
            width=400,   # Increased width
            fg_color="#000000", 
            text_color="#00FF00"
        )
        self.search_results.pack(pady=10)

        # Select All checkbox
        self.select_all_var = ctk.BooleanVar(value=False)
        select_all_checkbox = ctk.CTkCheckBox(
            right_column,
            text="Select All Scripts",
            variable=self.select_all_var,
            command=self.select_all_scripts,
            fg_color="#333333",
            hover_color="#444444"
        )
        select_all_checkbox.pack(pady=5)

        # Copy button
        copy_button = ctk.CTkButton(
            right_column,
            text="Copy Selected NSE",
            command=self.copy_nse_name,
            fg_color="#333333",
            hover_color="#444444"
        )
        copy_button.pack(pady=10)

        # Save Settings button
        save_button = ctk.CTkButton(
            right_column,
            text="Save Settings",
            command=self.save_settings,
            fg_color="#008000",
            hover_color="#00A000"
        )
        save_button.pack(pady=20)

    def update_nse_input(self):
        """Update NSE script input based on selected default option"""
        selected = self.default_nse_var.get()
        if selected == "all":
            self.nse_script_input.delete(0, "end")
            self.nse_script_input.insert(0, "/all")
            self.nse_script_input.configure(state="disabled")
        else:
            self.nse_script_input.configure(state="normal")
            self.nse_script_input.delete(0, "end")
            if "nse_scripts" in self.settings:
                self.nse_script_input.insert(0, self.settings["nse_scripts"])

    def open_nse_files(self):
        """Open NSE scripts directory"""
        nse_script_dir = "/usr/share/nmap/scripts/"
        webbrowser.open(nse_script_dir)

    def save_settings(self):
        """Save settings to file"""
        self.settings = {
            "nse_scripts": "/all" if self.default_nse_var.get() == "all" 
                          else self.nse_script_input.get().strip(),
            "timing_mode": self.timing_mode_var.get(),
            "nmap_user_agent": self.nmap_user_agent.get(),
            "nikto_user_agent": self.nikto_user_agent.get(),
            "default_nse_option": self.default_nse_var.get()
        }
        try:
            with open(self.settings_file, "w") as file:
                json.dump(self.settings, file, indent=4)
            messagebox.showinfo("Success", "Settings saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")

    def load_settings(self):
        """Load settings from file"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r") as file:
                    self.settings = json.load(file)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load settings: {str(e)}")
                self.settings = {}
        else:
            self.settings = {}

    def search_nse_scripts(self):
        """Search NSE scripts by keyword"""
        keyword = self.search_entry.get().strip().lower()
        if not keyword:
            self.search_results.delete("1.0", "end")
            self.search_results.insert("1.0", "Please enter a keyword to search.")
            return

        script_dir = "/usr/share/nmap/scripts"
        try:
            matching_scripts = [
                f for f in os.listdir(script_dir) 
                if keyword in f.lower() and f.endswith(".nse")
            ]
            if matching_scripts:
                self.search_results.delete("1.0", "end")
                self.search_results.insert("1.0", "\n".join(matching_scripts))
            else:
                self.search_results.delete("1.0", "end")
                self.search_results.insert("1.0", "No matching scripts found.")
        except FileNotFoundError:
            self.search_results.delete("1.0", "end")
            self.search_results.insert("1.0", "Script directory not found.")
        except Exception as e:
            self.search_results.delete("1.0", "end")
            self.search_results.insert("1.0", f"Error: {str(e)}")

    def select_all_scripts(self):
        """Select or deselect all NSE scripts"""
        if self.select_all_var.get():
            self.search_results.tag_add("sel", "1.0", "end")
            all_scripts = self.search_results.get("1.0", "end").strip()
            self.nse_script_input.delete(0, "end")
            self.nse_script_input.insert(0, all_scripts)
        else:
            self.search_results.tag_remove("sel", "1.0", "end")
            self.nse_script_input.delete(0, "end")

    def copy_nse_name(self):
        """Copy selected NSE script name"""
        try:
            selected_text = self.search_results.get("sel.first", "sel.last").strip()
            self.nse_script_input.delete(0, "end")
            self.nse_script_input.insert(0, selected_text)
            pyperclip.copy(selected_text)
            print(f"Copied NSE Script Name: {selected_text}")
        except Exception as e:
            print(f"Error copying NSE script name: {str(e)}")


if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Settings Tab")
    app.geometry("800x630")  # Increased window size
    SettingsTab(app)
    app.mainloop()
