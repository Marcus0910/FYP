import customtkinter as ctk
import subprocess
import threading
import xml.etree.ElementTree as ET
from tkinter import ttk, messagebox
import os
from datetime import datetime


class NmapScannerApp:
    def __init__(self, parent):
        self.parent = parent
        self.build_main_tab()

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
        """Perform the Nmap and Nikto scans"""
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

            # Run Nikto scan
            self.scan_results.extend(self.run_nikto_scan(target))

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
                nmap_results.append(("Nmap", port_id, protocol, state, name, f"{product} {version}".strip()))

                # Insert the scan result into the treeview
                self.tree.insert(
                    "",
                    "end",
                    values=("Nmap", port_id, protocol, state, name, f"{product} {version}".strip()),
                )

        return nmap_results

    def run_nikto_scan(self, target):
        """Run Nikto scan and return results"""
        nikto_results = []
        nikto_command = ["nikto", "-h", target, "-Format", "xml"]

        result = subprocess.run(nikto_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            raise Exception(f"Nikto error: {result.stderr}")

        root = ET.fromstring(result.stdout)
        for item in root.findall(".//item"):
            description = item.find("description").text.strip() if item.find("description") is not None else ""
            url = item.find("url").text.strip() if item.find("url") is not None else ""
            risk_level = item.find("risk").text.strip() if item.find("risk") is not None else ""

            # Add to scan results list
            nikto_results.append(("Nikto", url, risk_level, description, "", ""))

            # Insert the scan result into the treeview
            self.tree.insert(
                "",
                "end",
                values=("Nikto", url, risk_level, description, "", ""),
            )

        return nikto_results

    def generate_report(self):
        # Generate and save an HTML report with Nmap and Nikto command line outputs
        if not self.scan_results:
            self.show_error_message("Error", "No scan results to generate a report.")
            return

        output_file = os.path.join(os.getcwd(), "scan_report.html")
        target = self.target_input.get()
        ports = self.port_input.get().strip()

        try:
            # Get current timestamp
            current_time = datetime.now().strftime("%a %b %d %H:%M:%S %Y")
            
            # Run Nmap scan
            nmap_command = ["nmap", "--privileged", "-sV"]
            if ports:
                nmap_command.extend(["-p", ports])
            nmap_command.extend([target])
            
            nmap_process = subprocess.run(nmap_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            nmap_output = nmap_process.stdout

            # Run Nikto scan
            nikto_command = ["nikto", "-h", target]
            if ports:
                nikto_command.extend(["-p", ports])
            
            nikto_process = subprocess.run(nikto_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            nikto_output = nikto_process.stdout

            # Create HTML content
            html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Scan Report</title>
                <style>
                    body {{
                        font-family: monospace;
                        margin: 20px;
                        background-color: white;
                        color: black;
                        white-space: pre-wrap;
                        word-wrap: break-word;
                    }}
                    h1 {{
                        font-family: Arial, sans-serif;
                        font-size: 24px;
                        margin-bottom: 20px;
                    }}
                    h2 {{
                        font-family: Arial, sans-serif;
                        font-size: 20px;
                        margin-top: 30px;
                        margin-bottom: 10px;
                    }}
                    .output {{
                        font-family: monospace;
                        font-size: 14px;
                        line-height: 1.4;
                    }}
                </style>
            </head>
            <body>
                <h1>Scan Report</h1>
                
                <h2>Nmap Results:</h2>
                <div class="output">
    {nmap_output}
                </div>

                <h2>Nikto Results:</h2>
                <div class="output">
    {nikto_output}
                </div>
            </body>
            </html>
            """

            # Write the HTML content to a file
            with open(output_file, "w", encoding='utf-8') as file:
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
    NmapScannerApp(app)
    app.mainloop()
