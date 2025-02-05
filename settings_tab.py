import customtkinter as ctk
import webbrowser
import os
import pyperclip
import json
from tkinter import messagebox


class SettingsTab:
    def __init__(self, parent):
        self.parent = parent
        self.settings_file = "settings.json"  # 配置文件路径
        self.load_settings()  # 加载设置
        self.build_settings_tab()

    def build_settings_tab(self):
        """构建设置功能的界面"""
        main_frame = ctk.CTkFrame(self.parent, fg_color="#1A1A1A")  # 深灰背景
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 左右两列布局
        columns_frame = ctk.CTkFrame(main_frame, fg_color="#1A1A1A")  # 深灰背景
        columns_frame.pack(fill="both", expand=True)

        # 左列（Nmap 设置）
        left_column = ctk.CTkFrame(columns_frame, fg_color="#1A1A1A")  # 深灰背景
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Nmap Settings 标题
        ctk.CTkLabel(left_column, text="Nmap Settings", font=('Arial', 16, 'bold'), text_color="#00FF00").pack(pady=10)

        # 用户输入 NSE 脚本名字
        ctk.CTkLabel(left_column, text="Enter NSE Script Name:", text_color="#00FF00").pack(pady=5)
        self.nse_script_input = ctk.CTkEntry(left_column, placeholder_text="Enter NSE script name (e.g., http-title.nse)")
        self.nse_script_input.pack(pady=5)
        self.nse_script_input.insert(0, self.settings.get("nse_scripts", ""))  # 加载保存的设置

        # 添加打开 NSE 文件按钮
        nse_button = ctk.CTkButton(
            left_column,
            text="Open NSE Files",
            command=self.open_nse_files,
            fg_color="#333333",  # 深灰色按钮
            hover_color="#444444"  # 悬停时更浅的灰色
        )
        nse_button.pack(pady=5)

        # Timing Mode
        ctk.CTkLabel(left_column, text="Select Timing Mode (T1-T5):", text_color="#00FF00").pack(pady=5)
        self.timing_mode_var = ctk.StringVar(value=self.settings.get("timing_mode", "T1"))
        self.timing_mode_option = ctk.CTkOptionMenu(
            left_column,
            variable=self.timing_mode_var,
            values=["T1", "T2", "T3", "T4", "T5"],
            fg_color="#333333",  # 深灰色
            button_color="#333333",
            button_hover_color="#444444"  # 悬停时颜色
        )
        self.timing_mode_option.pack(pady=5)

        # User-Agent Settings 分组标题
        ctk.CTkLabel(left_column, text="User-Agent Settings", font=('Arial', 16, 'bold'), text_color="#00FF00").pack(pady=20)

        # Custom Nmap User-Agent
        ctk.CTkLabel(left_column, text="Custom Nmap User-Agent:", text_color="#00FF00").pack(pady=5)
        self.nmap_user_agent = ctk.StringVar(value=self.settings.get("nmap_user_agent", "Chrome"))
        self.nmap_user_agent_option = ctk.CTkOptionMenu(
            left_column,
            variable=self.nmap_user_agent,
            values=["Chrome", "Firefox", "Brave", "Edge"],
            fg_color="#333333",  # 深灰色
            button_color="#333333",
            button_hover_color="#444444"  # 悬停时颜色
        )
        self.nmap_user_agent_option.pack(pady=5)

        # Custom Nikto User-Agent
        ctk.CTkLabel(left_column, text="Custom Nikto User-Agent:", text_color="#00FF00").pack(pady=5)
        self.nikto_user_agent = ctk.StringVar(value=self.settings.get("nikto_user_agent", "Chrome"))
        self.nikto_user_agent_option = ctk.CTkOptionMenu(
            left_column,
            variable=self.nikto_user_agent,
            values=["Chrome", "Firefox", "Brave", "Edge"],
            fg_color="#333333",  # 深灰色
            button_color="#333333",
            button_hover_color="#444444"  # 悬停时颜色
        )
        self.nikto_user_agent_option.pack(pady=5)

        # 右列（包含搜索功能和 Save 按钮）
        right_column = ctk.CTkFrame(columns_frame, fg_color="#1A1A1A")  # 深灰背景
        right_column.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # Search NSE Scripts 标题
        ctk.CTkLabel(right_column, text="Search NSE Scripts", font=('Arial', 16, 'bold'), text_color="#00FF00").pack(pady=10)

        # 搜索框
        self.search_entry = ctk.CTkEntry(right_column, placeholder_text="Enter keyword")
        self.search_entry.pack(pady=5)

        # 搜索按钮
        search_button = ctk.CTkButton(
            right_column,
            text="Search",
            command=self.search_nse_scripts,
            fg_color="#333333",  # 深灰色
            hover_color="#444444"  # 悬停时颜色
        )
        search_button.pack(pady=5)

        # 搜索结果显示
        self.search_results = ctk.CTkTextbox(right_column, height=200, width=300, fg_color="#000000", text_color="#00FF00")  # 黑色背景，绿色文字
        self.search_results.pack(pady=10)

        # 添加 "Select All" 复选框
        self.select_all_var = ctk.BooleanVar(value=False)  # 默认未选中
        select_all_checkbox = ctk.CTkCheckBox(
            right_column,
            text="Select All Scripts",
            variable=self.select_all_var,
            command=self.select_all_scripts,
            fg_color="#333333",  # 深灰色
            hover_color="#444444"  # 悬停时更浅的灰色
        )
        select_all_checkbox.pack(pady=5)

        # 添加复制按钮
        copy_button = ctk.CTkButton(
            right_column,
            text="Copy Selected NSE",
            command=self.copy_nse_name,
            fg_color="#333333",  # 深灰色
            hover_color="#444444"  # 悬停时颜色
        )
        copy_button.pack(pady=10)

        # Save 按钮（自定义颜色）
        save_button = ctk.CTkButton(
            right_column,
            text="Save Settings",
            command=self.save_settings,
            fg_color="#008000",  # 深绿色按钮
            hover_color="#00A000"  # 悬停时更亮的绿色
        )
        save_button.pack(pady=20)

    def open_nse_files(self):
        """打开 NSE 脚本文件目录"""
        nse_script_dir = "/usr/share/nmap/scripts/"
        webbrowser.open(nse_script_dir)

    def save_settings(self):
        """保存设置到文件"""
        self.settings = {
            "nse_scripts": self.nse_script_input.get().strip(),
            "timing_mode": self.timing_mode_var.get(),
            "nmap_user_agent": self.nmap_user_agent.get(),
            "nikto_user_agent": self.nikto_user_agent.get(),
        }
        try:
            with open(self.settings_file, "w") as file:
                json.dump(self.settings, file, indent=4)
            messagebox.showinfo("Success", "Settings saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")

    def load_settings(self):
        """从文件加载设置"""
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
        """搜索 NSE 脚本关键字"""
        keyword = self.search_entry.get().strip().lower()
        if not keyword:
            self.search_results.delete("1.0", "end")
            self.search_results.insert("1.0", "Please enter a keyword to search.")
            return

        script_dir = "/usr/share/nmap/scripts"
        try:
            # 搜索包含关键字的脚本
            matching_scripts = [
                f for f in os.listdir(script_dir) if keyword in f.lower() and f.endswith(".nse")
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
        """选择或取消选择搜索结果中的所有 NSE 脚本，并自动填入到 NSE 输入框"""
        if self.select_all_var.get():
            # Select all scripts
            self.search_results.tag_add("sel", "1.0", "end")
            all_scripts = self.search_results.get("1.0", "end").strip()
            self.nse_script_input.delete(0, "end")
            self.nse_script_input.insert(0, all_scripts)
        else:
            # Deselect all scripts
            self.search_results.tag_remove("sel", "1.0", "end")
            self.nse_script_input.delete(0, "end")

    def copy_nse_name(self):
        """复制搜索结果中的 NSE 脚本名字到输入框"""
        try:
            selected_text = self.search_results.get("sel.first", "sel.last").strip()
            self.nse_script_input.delete(0, "end")
            self.nse_script_input.insert(0, selected_text)
            pyperclip.copy(selected_text)  # 复制到剪贴板
            print(f"Copied NSE Script Name: {selected_text}")
        except Exception as e:
            print(f"Error copying NSE script name: {str(e)}")


if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Settings Tab")
    app.geometry("800x600")
    SettingsTab(app)
    app.mainloop()
