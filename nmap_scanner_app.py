import customtkinter as ctk
import subprocess
import threading
import xml.etree.ElementTree as ET
from tkinter import ttk, messagebox


class NmapScannerApp:
    def __init__(self, parent):
        self.parent = parent
        self.build_main_tab()

    def build_main_tab(self):
        """构建 NmapScannerApp 界面"""
        self.tab_main = ctk.CTkFrame(self.parent)
        self.tab_main.pack(fill="both", expand=True)

        top_panel = ctk.CTkFrame(self.tab_main)
        top_panel.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(top_panel, text="Target:", font=("Arial", 12)).pack(side="left", padx=5)
        self.target_input = ctk.CTkEntry(top_panel, width=200, placeholder_text="Enter target (e.g. URL / 192.168.1.1)")
        self.target_input.pack(side="left", padx=5)

        self.scan_button = ctk.CTkButton(top_panel, text="Scan Ports", command=self.start_scan, width=100, height=30)
        self.scan_button.pack(side="left", padx=5)

        self.progress = ttk.Progressbar(self.tab_main, orient="horizontal", length=300, mode="indeterminate")
        self.progress.pack(pady=10)
        self.progress.pack_forget()

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
            columns=("Port", "Protocol", "State", "Service", "Version"),
            show="headings",
        )
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col.title(), anchor="center")
            self.tree.column(col, anchor="center", width=140)
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        scroll = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")

    def start_scan(self):
        """启动扫描"""
        self.progress.pack()
        self.progress.start(10)
        self.scan_button.configure(state="disabled")
        threading.Thread(target=self.perform_scan).start()

    def perform_scan(self):
        """执行 Nmap 扫描"""
        self.tree.delete(*self.tree.get_children())
        target = self.target_input.get()
        if not target:
            self.progress.stop()
            self.progress.pack_forget()
            self.scan_button["state"] = "normal"
            self.show_error_message("Error", "Please enter a target.")
            return
        try:
            nmap_command = ["nmap", "-sV", "-oX", "-", target]
            result = subprocess.run(nmap_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                self.progress.stop()
                self.progress.pack_forget()
                self.scan_button["state"] = "normal"
                self.show_error_message("Error", f"Nmap error: {result.stderr}")
                return

            nmap_output = result.stdout
            root = ET.fromstring(nmap_output)
            for host in root.findall("host"):
                for port in host.findall(".//port"):
                    port_id = port.get("portid")
                    protocol = port.get("protocol", "unknown")
                    state = port.find("state").get("state", "unknown")
                    service = port.find("service")
                    name = service.get("name", "") if service is not None else ""
                    product = service.get("product", "") if service is not None else ""
                    version = service.get("version", "") if service is not None else ""

                    self.tree.insert(
                        "",
                        "end",
                        values=(port_id, protocol, state, name, f"{product} {version}".strip()),
                    )

        except Exception as e:
            self.show_error_message("Error", f"An error occurred: {str(e)}")
        finally:
            self.progress.stop()
            self.progress.pack_forget()
            self.scan_button["state"] = "normal"

    def show_error_message(self, title, message):
        messagebox.showerror(title, message)
