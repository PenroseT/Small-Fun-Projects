import numpy as np
import tkinter as tk
import matplotlib.pyplot as plt
from datetime import datetime
import csv
import matplotlib.dates as mdates
from tkinter import filedialog, messagebox, ttk


plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['font.family'] = 'STIXGeneral'


def plot_pressure_data(data_file):
    
    datetimes = []
    blood_pressures_sys = []
    blood_pressures_dia = []
    heart_rates = []
    
    # Read data from CSV file
    with open(data_file, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header
        for row in reader:
            date_str, time_str, bp_sys, bp_dia, hr = row
            datetime_obj = datetime.strptime(date_str + " " + time_str, "%Y-%m-%d %H:%M")
            datetimes.append(datetime_obj)
            blood_pressures_sys.append(float(bp_sys))
            blood_pressures_dia.append(float(bp_dia))
            heart_rates.append(float(hr))
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(datetimes, blood_pressures_sys, marker='o', linestyle='-', lw=2)
    ax.plot(datetimes, blood_pressures_dia, marker='o', linestyle='-', lw=2)
    #plt.plot(datetimes, heart_rates, marker='o', linestyle='-')
    ax.set_xlabel("Time", fontsize=30)
    ax.set_ylabel("Blood Pressure [mmHg]", fontsize=30)
    ax.set_title("Blood pressure over time", fontsize=40)
    #lt.xticks(rotation=45)
    ax.tick_params(axis="both", labelsize=15)

    date_diff = datetimes[len(datetimes)-1]-datetimes[0]
    hour_diff = int(np.floor(date_diff.total_seconds()/3600))    

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d, %Y, %H:%M'))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=int(np.floor(hour_diff/6))))  # Adjust tick frequency
    plt.xticks(rotation=45, ha='right')
    
    plt.grid()
    plt.tight_layout()
    plt.show()

def plot_wrapper():
    data_file = "blood_pressure.csv"
    plot_pressure_data(data_file)

def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    
    if not file_path:
        return
    
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)
        
    for row in tree.get_children():
        tree.delete(row)
    
    tree["columns"] = rows[0]
    tree.heading("#0", text="Entry")
    
    for col in rows[0]:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    
    for i, row in enumerate(rows[1:], start=1):
        tree.insert("", "end", text=str(i), values=row)

    global path_overwrite
    path_overwrite = file_path

def save_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return
    
    rows = []
    for item in tree.get_children():
        rows.append(tree.item(item)['values'])
    
    with open(file_path, "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(tree["columns"])
        writer.writerows(rows)
    
    messagebox.showinfo("Success", "File saved successfully!")

def overwrite_file(file_path):    
    rows = []
    for item in tree.get_children():
        rows.append(tree.item(item)['values'])
    
    with open(file_path, "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(tree["columns"])
        writer.writerows(rows)
    
    messagebox.showinfo("Success", "File saved successfully!")

def add_row():
    
    def submit():
        values = [entry.get() for entry in entries]
        tree.insert("", "end", values=values)
        add_window.destroy()
        
    def submit_and_overwrite():
        values = [entry.get() for entry in entries]
        tree.insert("", "end", values=values)
        overwrite_file(path_overwrite)
        add_window.destroy()
    
    add_window = tk.Toplevel(root)
    add_window.title("Add Measurement")
    add_window.geometry("350x220")
    
    entries = []
    for idx, col in enumerate(tree["columns"]):
        tk.Label(add_window, text=col).grid(row=idx, column=0, padx=5, pady=5)
        entry = tk.Entry(add_window)
        entry.grid(row=idx, column=1, padx=5, pady=5)
        entries.append(entry)
    
    submit_button = ttk.Button(add_window, text="Submit", command=submit)
    submit_button.grid(row=len(tree["columns"]), column=0, columnspan=1, pady=10)
    
    submit_overwrite_button = ttk.Button(add_window, text="Submit and Overwrite", command=submit_and_overwrite)
    submit_overwrite_button.grid(row=len(tree["columns"]), column=1, columnspan=1, pady=10)

def delete_selected():
    selected_items = tree.selection()
    for item in selected_items:
        tree.delete(item)

root = tk.Tk()
root.title("BPlotter")
root.geometry("600x400")

frame = ttk.Frame(root, padding=10)
frame.pack(fill=tk.BOTH, expand=True)

button_frame = ttk.Frame(frame)
button_frame.pack(fill=tk.X)

ttk.Button(button_frame, text="Open CSV", command=open_file).pack(side=tk.LEFT, padx=5)
ttk.Button(button_frame, text="Save CSV", command=save_file).pack(side=tk.LEFT, padx=5)
ttk.Button(button_frame, text="Add Measurement", command=add_row).pack(side=tk.LEFT, padx=5)
ttk.Button(button_frame, text="Delete Selected", command=delete_selected).pack(side=tk.LEFT, padx=5)

tree = ttk.Treeview(frame, show="headings")
tree.pack(fill=tk.BOTH, expand=True)

plot_button_frame = ttk.Frame(root, padding=5)
plot_button_frame.pack(fill=tk.BOTH)
ttk.Button(plot_button_frame, text="Plot", command=plot_wrapper).pack(side=tk.RIGHT, padx=5)

if __name__ == "__main__":
    root.mainloop()
