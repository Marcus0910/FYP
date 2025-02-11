import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector  # Using MySQL for the scanresults table

# Database configuration
DATABASE_CONFIG = {
    'user': 'root',
    'password': 'mysql_YRARJz',
    'host': '157.173.126.210',  # MySQL server's IP address
    'database': 'pythonfyp',
    'port': 3306,
}


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
        delete_button.pack(side="right", padx=5)

        # Add the Refresh button
        refresh_button = tk.Button(
            label_frame,
            text="Refresh",
            font=("Arial", 12, "bold"),
            bg="#007BFF",  # Blue button
            fg="white",
            activebackground="#0056b3",  # Darker blue on hover
            activeforeground="white",
            command=self.refresh_table,  # Function to refresh the table
        )
        refresh_button.pack(side="right", padx=5)

        # Add the Compare button
        compare_button = tk.Button(
            label_frame,
            text="Compare",
            font=("Arial", 12, "bold"),
            bg="#28a745",  # Green button
            fg="white",
            activebackground="#218838",  # Darker green on hover
            activeforeground="white",
            command=self.compare_selected_rows,  # Function to compare selected rows
        )
        compare_button.pack(side="right", padx=5)

        # Create a treeview to display the history
        columns = ("ScanID", "Tool", "PortURL", "RiskLevel", "Description", "Service", "Version", "ScanTime")
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
        """Load history records from the MySQL scanresults table."""
        try:
            # Connect to the MySQL database using DATABASE_CONFIG
            connection = mysql.connector.connect(**DATABASE_CONFIG)
            cursor = connection.cursor()

            # Query to fetch data from the scanresults table
            query = """
                SELECT ScanID, Tool, PortURL, RiskLevel, Description, Service, Version, ScanTime
                FROM scanresults
            """
            cursor.execute(query)
            rows = cursor.fetchall()

            # Insert rows into the Treeview
            for row in rows:
                self.history_table.insert("", "end", values=row)

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error fetching data: {err}")
        finally:
            if connection.is_connected():
                cursor.close()
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
        """Delete a record from the MySQL scanresults table."""
        try:
            # Connect to the MySQL database using DATABASE_CONFIG
            connection = mysql.connector.connect(**DATABASE_CONFIG)
            cursor = connection.cursor()

            query = "DELETE FROM scanresults WHERE ScanID = %s"
            cursor.execute(query, (record_id,))
            connection.commit()

        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Failed to delete record: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def refresh_table(self):
        """Clear and reload the history table."""
        self.history_table.delete(*self.history_table.get_children())
        self.load_history()

    def compare_selected_rows(self):
        """Compare two selected rows and display differences in a user-friendly format."""
        selected_items = self.history_table.selection()
        if len(selected_items) != 2:
            messagebox.showwarning("Selection Error", "Please select exactly two rows to compare.")
            return

        # Get the data for the selected rows
        row1 = self.history_table.item(selected_items[0], "values")
        row2 = self.history_table.item(selected_items[1], "values")
        columns = self.history_table["columns"]

        # Find differences between the rows
        differences = []
        for i, col in enumerate(columns):
            if row1[i] != row2[i]:
                differences.append(f"{col}:\n    Row 1: {row1[i]}\n    Row 2: {row2[i]}")

        # Display the results
        if differences:
            diff_message = "\n\n".join(differences)
            messagebox.showinfo("Row Comparison", f"Differences:\n\n{diff_message}")
        else:
            messagebox.showinfo("Row Comparison", "The selected rows are identical.")


# Example Usage
if __name__ == "__main__":
    root = tk.Tk()
    root.title("History Tab Example")
    root.geometry("800x600")

    history_tab = HistoryTab(root)

    root.mainloop()
