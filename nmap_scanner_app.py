import customtkinter as ctk
import subprocess
import threading
import xml.etree.ElementTree as ET
from tkinter import ttk, messagebox
import os
import mysql.connector
import json  # For reading settings.json
from datetime import datetime
import queue

# MySQL Database configuration
DATABASE_CONFIG = {
    'user': 'root',
    'password': 'mysql_YRARJz',
    'host': '157.173.126.210',  # MySQL server's IP address
    'database': 'pythonfyp',
    'port': 3306,
}


class NmapScannerApp:
    def __init__(self, parent):
        self.parent = parent
        self.build_main_tab()
        self.db_queue = queue.Queue()  # Queue for database operations
        self.connect_to_database()
        self.start_database_worker()

    def connect_to_database(self):
        """Connect to the MySQL database and create the scanresults table if it doesn't exist."""
        try:
            self.conn = mysql.connector.connect(**DATABASE_CONFIG)
            self.cursor = self.conn.cursor()

            # Create the scanresults table if it doesn't already exist
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS scanresults (
                ScanID INT AUTO_INCREMENT PRIMARY KEY,
                Tool VARCHAR(50),
                PortURL VARCHAR(255),
                RiskLevel VARCHAR(50),
                Description TEXT,
                Service VARCHAR(255),
                Version VARCHAR(255),
                ScanTime DATETIME
            )
            """)
            self.conn.commit()

        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Failed to connect to the database: {str(e)}")
            self.conn = None

    def start_database_worker(self):
        """Start a thread to process database operations from the queue."""
        self.worker_thread = threading.Thread(target=self.database_worker, daemon=True)
        self.worker_thread.start()

    def database_worker(self):
        """Process database operations from the queue."""
        while True:
            task = self.db_queue.get()  # Get a task from the queue
            if task is None:  # Exit if None is received
                break

            # Perform the database operation
            try:
                tool, port_url, risk_level, description, service, version = task
                scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.cursor.execute("""
                INSERT INTO scanresults (Tool, PortURL, RiskLevel, Description, Service, Version, ScanTime)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (tool, port_url, risk_level, description, service, version, scan_time))
                self.conn.commit()
            except mysql.connector.Error as e:
                messagebox.showerror("Database Error", f"Failed to save data: {str(e)}")

        # Close the database connection when done
        if self.conn:
            self.conn.close()

    def build_main_tab(self):
        """Build the main tab for Nmap scanner"""
        self.tab_main = ctk.CTkFrame(self.parent)
        self.tab_main.pack(fill="both", expand=True)

        # Top panel for target input and scan button
        top_panel = ctk.CTkFrame(self.tab_main)
        top_panel.pack(pady=10, padx=10, fill="x")

        # Target input
        ctk.CTkLabel(top_panel, text="Target:", font=("Arial", 12)).pack(side="left", padx=5)
        self.target_input = ctk.CTkEntry(top_panel, width=200, placeholder_text="Enter target (e.g., URL / 192.168.1.1)")
        self.target_input.pack(side="left", padx=5)

        # Port input
        ctk.CTkLabel(top_panel, text="Ports (optional):", font=("Arial", 12)).pack(side="left", padx=5)
        self.port_input = ctk.CTkEntry(top_panel, width=150, placeholder_text="e.g., 22,80,443")
        self.port_input.pack(side="left", padx=5)

        # Scan button
        self.scan_button = ctk.CTkButton(top_panel, text="Scan Ports", command=self.start_scan, width=100, height=30)
        self.scan_button.pack(side="left", padx=5)

        # Report button
        self.report_button = ctk.CTkButton(top_panel, text="Generate Report", command=self.generate_report, width=150, height=30)
        self.report_button.pack(side="left", padx=5)
        self.report_button.configure(state="disabled")  # Disabled initially

        # Progress bar
        self.progress = ttk.Progressbar(self.tab_main, orient="horizontal", length=300, mode="indeterminate")
        self.progress.pack(pady=10)
        self.progress.pack_forget()  # Hidden initially

        # Treeview to display scan results
        self.tree_frame = ctk.CTkFrame(self.tab_main)
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background="#D3D3D3",
            foreground="black",
            rowheight=25,
            font=("Arial", 10),
        )
        style.configure(
            "Treeview.Heading",
            background="#A9A9A9",
            foreground="black",
            font=("Arial", 11, "bold"),
        )
        style.map("Treeview", background=[("selected", "#6A5ACD")])

        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=("Tool", "Port/URL", "Risk Level", "Description", "Service", "Version"),
            show="headings",
        )
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col.title(), anchor="center")
            self.tree.column(col, anchor="center", width=140)
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Vertical scrollbar for the treeview
        scroll = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")

    def start_scan(self):
        """Start the scan in a separate thread"""
        self.progress.pack()
        self.progress.start(10)  # Start the progress bar animation
        self.scan_button.configure(state="disabled")  # Disable the button during scan
        self.report_button.configure(state="disabled")  # Disable the report button
        threading.Thread(target=self.perform_scan).start()

    def perform_scan(self):
        """Perform the Nmap scan"""
        # Clear previous results
        self.tree.delete(*self.tree.get_children())
        self.scan_results = []  # To store results for HTML report
        target = self.target_input.get()
        ports = self.port_input.get().strip()  # Get the user-specified ports

        if not target:
            self.progress.stop()
            self.progress.pack_forget()
            self.scan_button["state"] = "normal"
            self.show_error_message("Error", "Please enter a target.")
            return

        try:
            # Run Nmap scan
            self.scan_results.extend(self.run_nmap_scan(target, ports))

        except Exception as e:
            self.show_error_message("Error", f"An error occurred: {str(e)}")
        finally:
            self.progress.stop()
            self.progress.pack_forget()
            self.scan_button["state"] = "normal"  # Re-enable the button after the scan
            if self.scan_results:
                self.report_button.configure(state="normal")  # Enable the report button if there are results

    def run_nmap_scan(self, target, ports):
        """Run Nmap scan and return results"""
        nmap_results = []
        nmap_command = ["nmap", "-sV", "-oX", "-", target]
        if ports:  # Add ports to the command if specified
            nmap_command += ["-p", ports]

        result = subprocess.run(nmap_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            raise Exception(f"Nmap error: {result.stderr}")

        root = ET.fromstring(result.stdout)
        for host in root.findall("host"):
            for port in host.findall(".//port"):
                port_id = port.get("portid")
                protocol = port.get("protocol", "unknown")
                state = port.find("state").get("state", "unknown")
                service = port.find("service")
                name = service.get("name", "") if service is not None else ""
                product = service.get("product", "") if service is not None else ""
                version = service.get("version", "") if service is not None else ""

                # Add to scan results list
                nmap_results.append(("Nmap", port_id, state, "", name, f"{product} {version}".strip()))

                # Queue the result for saving to the database
                self.db_queue.put(("Nmap", port_id, state, "", name, f"{product} {version}".strip()))

                # Insert the scan result into the treeview
                self.tree.insert(
                    "",
                    "end",
                    values=("Nmap", port_id, state, "", name, f"{product} {version}".strip()),
                )

        return nmap_results

    def generate_report(self):
        """Generate and save an HTML report, including the scan settings."""
        if not self.scan_results:
            self.show_error_message("Error", "No scan results to generate a report.")
            return

        output_file = os.path.join(os.getcwd(), "scan_report.html")

        try:
            # Fetch settings from the settings file or current configuration
            settings = {}
            settings_file = "settings.json"
            if os.path.exists(settings_file):
                with open(settings_file, "r") as file:
                    settings = json.load(file)

            # Prepare HTML content
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Scan Report</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        margin: 20px;
                        line-height: 1.6;
                    }
                    h1, h2 {
                        color: #333;
                    }
                    table {
                        border-collapse: collapse;
                        width: 100%;
                        margin-top: 20px;
                    }
                    table, th, td {
                        border: 1px solid #ddd;
                    }
                    th, td {
                        padding: 8px;
                        text-align: left;
                    }
                    th {
                        background-color: #f2f2f2;
                    }
                    .settings {
                        background-color: #f9f9f9;
                        padding: 10px;
                        border: 1px solid #ddd;
                        margin-bottom: 20px;
                    }
                </style>
            </head>
            <body>
                <h1>Scan Report</h1>
            """

            # Add settings section
            html_content += """
            <h2>Scan Settings</h2>
            <div class="settings">
                <p><b>NSE Scripts:</b> {nse_scripts}</p>
                <p><b>Timing Mode:</b> {timing_mode}</p>
                <p><b>Nmap User-Agent:</b> {nmap_user_agent}</p>
                <p><b>Nikto User-Agent:</b> {nikto_user_agent}</p>
            </div>
            """.format(
                nse_scripts=settings.get("nse_scripts", "Not specified"),
                timing_mode=settings.get("timing_mode", "Not specified"),
                nmap_user_agent=settings.get("nmap_user_agent", "Not specified"),
                nikto_user_agent=settings.get("nikto_user_agent", "Not specified"),
            )

            # Add results table
            html_content += """
            <h2>Scan Results</h2>
            <table>
                <tr>
                    <th>Tool</th>
                    <th>Port/URL</th>
                    <th>Risk Level</th>
                    <th>Description</th>
                    <th>Service</th>
                    <th>Version</th>
                    <th>Scan Time</th>
                </tr>
            """

            # Fetch scan results from the database
            self.cursor.execute("SELECT * FROM scanresults")
            rows = self.cursor.fetchall()
            for row in rows:
                html_content += f"<tr><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td><td>{row[7]}</td></tr>"

            html_content += """
            </table>
            </body>
            </html>
            """

            # Write the HTML content to a file
            with open(output_file, "w") as file:
                file.write(html_content)

            messagebox.showinfo("Success", f"Report generated successfully: {output_file}")

        except Exception as e:
            self.show_error_message("Error", f"Failed to generate report: {str(e)}")

    def show_error_message(self, title, message):
        """Show an error message dialog"""
        messagebox.showerror(title, message)


if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Vulnerability Scanner")
    app.geometry("800x600")
    scanner_app = NmapScannerApp(app)

    # Ensure database connection is closed and worker thread is stopped when exiting
    def on_closing():
        scanner_app.db_queue.put(None)  # Signal the worker thread to exit
        scanner_app.worker_thread.join()  # Wait for the thread to finish
        app.destroy()

    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.mainloop()
