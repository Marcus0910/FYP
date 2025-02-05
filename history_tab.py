import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from config import DATABASE_CONFIG


class HistoryTab:
    def __init__(self, parent):
        self.parent = parent
        self.build_history_tab()

    def build_history_tab(self):
        """Build the history tab interface."""
        # Main frame with dark background
        frame = tk.Frame(self.parent, bg="#1e1e1e")  # Dark background
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Scanning History label
        label_frame = tk.Frame(frame, bg="#1e1e1e")  # Dark background
        label_frame.pack(fill="x", pady=10)

        tk.Label(
            label_frame,
            text="Scanning History",
            font=("Arial", 24, "bold"),
            bg="#1e1e1e",
            fg="#00ff00",  # Bright green text
        ).pack(side="left", padx=10)

        # Add the Delete button
        delete_button = tk.Button(
            label_frame,
            text="Delete",
            font=("Arial", 12, "bold"),
            bg="#ff4c4c",  # Red button
            fg="white",
            activebackground="#ff3333",  # Lighter red on hover
            activeforeground="white",
            command=self.delete_selected_row,  # Function to delete selected rows
        )
        delete_button.pack(side="right", padx=10)

        # Add the Compare button
        compare_button = tk.Button(
            label_frame,
            text="Compare",
            font=("Arial", 12, "bold"),
            bg="#4CAF50",  # Green button
            fg="white",
            activebackground="#45a049",  # Darker green on hover
            activeforeground="white",
            command=self.compare_selected_rows,  # Function to compare selected rows
        )
        compare_button.pack(side="right", padx=10)

        # Create a treeview to display the history
        columns = ("ID", "Target", "Port", "Protocol", "State", "Service", "Version", "Scan Time")
        self.history_table = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        self.history_table.pack(fill="both", expand=True, padx=10, pady=10)

        # Apply custom styles for the Treeview
        style = ttk.Style()
        style.theme_use("clam")  # Use a clean theme for compatibility
        style.configure(
            "Treeview",
            background="#333333",  # Dark gray background
            foreground="white",  # White text
            rowheight=25,
            fieldbackground="#333333",
            font=("Arial", 10),
        )
        style.configure(
            "Treeview.Heading",
            background="#444444",  # Slightly lighter gray for headers
            foreground="#00ff00",  # Bright green headers
            font=("Arial", 11, "bold"),
        )
        style.map(
            "Treeview",
            background=[("selected", "#6A5ACD")],  # Purple selection
            foreground=[("selected", "white")],
        )

        # Set the column headers
        for col in columns:
            self.history_table.heading(col, text=col)
            self.history_table.column(col, width=100, anchor="center")

        # Add a scrollbar
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.history_table.yview)
        self.history_table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Load data from the database
        self.load_history()

    def load_history(self):
        """Load history records from the database."""
        try:
            connection = mysql.connector.connect(**DATABASE_CONFIG)
            cursor = connection.cursor()

            query = "SELECT ScanID, target, port, protocol, state, service, version, scan_time FROM ScanResults"
            cursor.execute(query)
            rows = cursor.fetchall()

            for row in rows:
                self.history_table.insert("", "end", values=row)

        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            if cursor:
                cursor.close()
            if connection.is_connected():
                connection.close()

    def delete_selected_row(self):
        """Delete selected history records."""
        selected_items = self.history_table.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a record to delete.")
            return
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected record(s)?")
        if not confirm:
            return
        for item in selected_items:
            record_id = self.history_table.item(item, "values")[0]
            self.delete_from_database(record_id)
            self.history_table.delete(item)

    def delete_from_database(self, record_id):
        """Delete a record from the database."""
        try:
            connection = mysql.connector.connect(**DATABASE_CONFIG)
            cursor = connection.cursor()

            query = "DELETE FROM ScanResults WHERE ScanID = %s"
            cursor.execute(query, (record_id,))
            connection.commit()

        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to delete record: {e}")
        finally:
            if cursor:
                cursor.close()
            if connection.is_connected():
                connection.close()

    def compare_selected_rows(self):
        """Compare the selected rows in the history table."""
        selected_items = self.history_table.selection()  # Get selected rows
        if len(selected_items) < 2:
            messagebox.showinfo("Compare", "Please select at least two rows to compare.")
            return

        # Fetch data from selected rows
        selected_data = []
        for item in selected_items:
            selected_data.append(self.history_table.item(item, "values"))

        # Display comparison data
        comparison_window = tk.Toplevel(self.parent)
        comparison_window.title("Comparison Result")
        comparison_window.geometry("700x400")
        comparison_window.configure(bg="#1e1e1e")  # Dark background

        tk.Label(
            comparison_window,
            text="Comparison Result",
            font=("Arial", 18, "bold"),
            bg="#1e1e1e",
            fg="#00ff00",  # Bright green text
        ).pack(pady=10)

        # Create a treeview in the comparison window
        columns = ("ID", "Target", "Port", "Protocol", "State", "Service", "Version", "Scan Time")
        comparison_table = ttk.Treeview(comparison_window, columns=columns, show="headings", height=10)
        comparison_table.pack(fill="both", expand=True, padx=10, pady=10)

        # Apply the same style to the comparison table
        comparison_table["style"] = "Treeview"

        # Set the column headers
        for col in columns:
            comparison_table.heading(col, text=col)
            comparison_table.column(col, width=100, anchor="center")

        # Insert selected data into the comparison table
        for row in selected_data:
            comparison_table.insert("", "end", values=row)

        # Add a Close button
        close_button = tk.Button(
            comparison_window,
            text="Close",
            font=("Arial", 12, "bold"),
            bg="#444444",  # Dark button
            fg="white",
            activebackground="#555555",  # Slightly lighter on hover
            activeforeground="white",
            command=comparison_window.destroy,
        )
        close_button.pack(pady=10)