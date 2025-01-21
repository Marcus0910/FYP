import os
import subprocess
import sys
import customtkinter as ctk


class InstallerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Setup Installer")
        self.geometry("600x400")
        self.configure(bg="#1E1E1E")

        # UI 标题
        self.title_label = ctk.CTkLabel(self, text="Welcome to the Setup Installer", font=("Arial", 20, "bold"), text_color="green")
        self.title_label.pack(pady=20)

        # 描述信息
        self.description_label = ctk.CTkLabel(
            self,
            text="This installer will guide you through the installation process.\n"
                 "We will also need permission to modify file permissions (chmod).\n"
                 "Click 'Install' to proceed.",
            font=("Arial", 14),
            text_color="white",
            justify="center",
        )
        self.description_label.pack(pady=20)

        # 同意修改权限的复选框
        self.permission_var = ctk.BooleanVar(value=False)
        self.permission_checkbox = ctk.CTkCheckBox(
            self,
            text="I agree to modify system file permissions (chmod)",
            variable=self.permission_var,
            font=("Arial", 12),
            text_color="white",
            hover_color="green",
        )
        self.permission_checkbox.pack(pady=10)

        # 安装按钮
        self.install_button = ctk.CTkButton(
            self,
            text="Install",
            command=self.start_installation,
            fg_color="green",
            hover_color="#00A000",
            font=("Arial", 14, "bold"),
        )
        self.install_button.pack(pady=20)

        # 状态显示
        self.status_label = ctk.CTkLabel(self, text="", font=("Arial", 12), text_color="yellow")
        self.status_label.pack(pady=5)

    def start_installation(self):
        """启动安装过程"""
        if not self.permission_var.get():
            self.status_label.configure(text="You must agree to modify file permissions!", text_color="red")
            return

        self.status_label.configure(text="Installing...", text_color="yellow")
        self.update()

        try:
            # 执行 setup.py 安装
            self.run_setup()

            # 修改权限（示例：将 main.py 设置为可执行）
            self.change_permissions()

            # 删除安装界面文件
            self.cleanup_files()

            self.status_label.configure(text="Installation completed successfully!", text_color="green")
        except Exception as e:
            self.status_label.configure(text=f"Installation failed: {str(e)}", text_color="red")

    def run_setup(self):
        """运行 setup.py 安装"""
        if not os.path.exists("setup.py"):
            raise FileNotFoundError("setup.py not found in the current directory.")
        subprocess.check_call([sys.executable, "setup.py", "install"])

    def change_permissions(self):
        """更改文件权限"""
        main_file = "main.py"
        if os.path.exists(main_file):
            os.chmod(main_file, 0o755)  # 设置 main.py 为可执行权限
        else:
            raise FileNotFoundError(f"{main_file} not found to modify permissions.")

    def cleanup_files(self):
        """删除安装界面文件，保留 main.py"""
        current_file = os.path.basename(__file__)
        if os.path.exists(current_file):
            os.remove(current_file)


if __name__ == "__main__":
    app = InstallerApp()
    app.mainloop()