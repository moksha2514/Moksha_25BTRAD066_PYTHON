import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import date
import matplotlib.pyplot as plt

# DATABASE CONNECTION
conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    expense_date TEXT,
    category TEXT,
    description TEXT,
    amount REAL
)
""")

conn.commit()

# MAIN WINDOW
root = tk.Tk()
root.title("Personal Expense Tracker")
root.geometry("850x600")

title = tk.Label(
    root,
    text="PERSONAL EXPENSE TRACKER",
    font=("Arial", 20, "bold")
)
title.pack(pady=15)

# INPUT FRAME
frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Category:").grid(row=0, column=0, padx=10, pady=5)

category_box = ttk.Combobox(
    frame,
    values=["Food", "Travel", "Education", "Shopping", "Bills", "Other"],
    state="readonly"
)
category_box.grid(row=0, column=1, padx=10)
category_box.set("Food")

tk.Label(frame, text="Description:").grid(row=1, column=0, padx=10, pady=5)

description_entry = tk.Entry(frame, width=25)
description_entry.grid(row=1, column=1, padx=10)

tk.Label(frame, text="Amount (Rs.):").grid(row=2, column=0, padx=10, pady=5)

amount_entry = tk.Entry(frame, width=25)
amount_entry.grid(row=2, column=1, padx=10)


# ADD EXPENSE FUNCTION
def add_expense():

    category = category_box.get()
    description = description_entry.get().strip()
    amount_text = amount_entry.get().strip()

    if description == "" or amount_text == "":
        messagebox.showwarning("Warning", "Please fill all fields")
        return

    try:
        amount = float(amount_text)

        if amount <= 0:
            messagebox.showwarning(
                "Warning", "Amount must be greater than zero"
            )
            return

    except ValueError:
        messagebox.showerror("Error", "Enter a valid amount")
        return

    cursor.execute("""
    INSERT INTO expenses
    (expense_date, category, description, amount)
    VALUES (?, ?, ?, ?)
    """, (date.today().isoformat(), category, description, amount))

    conn.commit()

    messagebox.showinfo("Success", "Expense added successfully!")

    description_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)

    view_expenses()
    calculate_total()


# VIEW EXPENSES FUNCTION
def view_expenses():

    for item in tree.get_children():
        tree.delete(item)

    cursor.execute("SELECT * FROM expenses ORDER BY id DESC")

    records = cursor.fetchall()

    for row in records:
        tree.insert("", tk.END, values=row)


# DELETE EXPENSE FUNCTION
def delete_expense():

    selected = tree.selection()

    if not selected:
        messagebox.showwarning("Warning", "Select an expense to delete")
        return

    item = tree.item(selected[0])
    expense_id = item["values"][0]

    cursor.execute(
        "DELETE FROM expenses WHERE id = ?",
        (expense_id,)
    )

    conn.commit()

    messagebox.showinfo("Success", "Expense deleted successfully!")

    view_expenses()
    calculate_total()


# CALCULATE TOTAL EXPENSES
def calculate_total():

    cursor.execute("SELECT SUM(amount) FROM expenses")

    total = cursor.fetchone()[0]

    if total is None:
        total = 0

    total_label.config(
        text=f"Total Expenses: Rs. {total:.2f}"
    )


# CATEGORY-WISE EXPENSE CHART
def show_chart():

    cursor.execute("""
    SELECT category, SUM(amount)
    FROM expenses
    GROUP BY category
    """)

    data = cursor.fetchall()

    if not data:
        messagebox.showwarning("Warning", "No expenses available")
        return

    categories = [row[0] for row in data]
    amounts = [row[1] for row in data]

    plt.figure(figsize=(7, 5))

    plt.pie(
        amounts,
        labels=categories,
        autopct="%1.1f%%",
        startangle=90
    )

    plt.title("Category-wise Expense Analysis")
    plt.show()


# BUTTON FRAME
button_frame = tk.Frame(root)
button_frame.pack(pady=15)

tk.Button(
    button_frame,
    text="Add Expense",
    command=add_expense,
    width=15
).grid(row=0, column=0, padx=5)

tk.Button(
    button_frame,
    text="View Expenses",
    command=view_expenses,
    width=15
).grid(row=0, column=1, padx=5)

tk.Button(
    button_frame,
    text="Delete Expense",
    command=delete_expense,
    width=15
).grid(row=0, column=2, padx=5)

tk.Button(
    button_frame,
    text="Show Expense Chart",
    command=show_chart,
    width=18
).grid(row=0, column=3, padx=5)


# EXPENSE TABLE
tree = ttk.Treeview(
    root,
    columns=("ID", "Date", "Category", "Description", "Amount"),
    show="headings"
)

tree.heading("ID", text="ID")
tree.heading("Date", text="Date")
tree.heading("Category", text="Category")
tree.heading("Description", text="Description")
tree.heading("Amount", text="Amount")

tree.column("ID", width=50)
tree.column("Date", width=120)
tree.column("Category", width=120)
tree.column("Description", width=250)
tree.column("Amount", width=120)

tree.pack(fill="both", expand=True, padx=15, pady=15)


# TOTAL EXPENSE LABEL
total_label = tk.Label(
    root,
    text="Total Expenses: Rs. 0.00",
    font=("Arial", 16, "bold")
)

total_label.pack(pady=15)


# INITIAL DISPLAY
view_expenses()
calculate_total()

# RUN APPLICATION
root.mainloop()

conn.close()
