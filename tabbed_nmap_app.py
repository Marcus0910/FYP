import customtkinter as ctk
from settings_tab import SettingsTab  # 导入设置功能模块
from history_tab import HistoryTab  # 导入历史记录模块
from nmap_scanner_app import NmapScannerApp  # 导入 Nmap 扫描模块


class TabbedNmapApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Nmap Scanner")
        self.root.geometry("1200x750")
        self.root.resizable(False, False)

        # 创建 Tab 视图
        self.tab_view = ctk.CTkTabview(self.root)
        self.tab_view.pack(fill="both", expand=True)

        # 添加 Tabs
        self.main_tab = self.tab_view.add("Main")
        self.settings_tab = self.tab_view.add("Settings")
        self.history_tab = self.tab_view.add("History")
        self.help_tab = self.tab_view.add("Help")

        # 初始化各个 Tab 页面
        self.build_main_tab()
        self.build_settings_tab()
        self.build_history_tab()
        self.build_help_tab()

    def build_main_tab(self):
        """构建主扫描功能的 Tab 页面"""
        self.nmap_scanner = NmapScannerApp(self.main_tab)  # 使用 NmapScannerApp 构建扫描功能

    def build_settings_tab(self):
        """构建设置的 Tab 页面"""
        self.settings = SettingsTab(self.settings_tab)  # 使用 SettingsTab 构建设置功能

    def build_history_tab(self):
        """构建历史记录的 Tab 页面"""
        self.history = HistoryTab(self.history_tab)  # 使用 HistoryTab 构建历史记录功能

    def build_help_tab(self):
        """构建帮助的 Tab 页面"""
        frame = ctk.CTkFrame(self.help_tab)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="Help & Documentation", font=("Arial", 24, "bold")).pack(pady=10)

        help_text = (
            "Welcome to the Advanced Nmap Scanner!\n\n"
            "Main Tab:\n"
            "- Perform port scans and view results.\n\n"
            "Settings Tab:\n"
            "- Configure app settings and preferences.\n\n"
            "History Tab:\n"
            "- View past scan results.\n\n"
            "Help Tab:\n"
            "- Access documentation and guidance.\n\n"
            "For more information, visit our website or contact support."
        )

        help_box = ctk.CTkTextbox(frame, wrap="word", height=400)
        help_box.insert("1.0", help_text)
        help_box.configure(state="disabled")
        help_box.pack(fill="both", expand=True, padx=10, pady=10)
