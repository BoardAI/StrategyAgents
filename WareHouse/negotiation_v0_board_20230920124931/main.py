'''
This is the main file that will run the negotiation strategy report software. 
It imports the necessary modules and runs the main function.
'''
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import pandas as pd
import negotiation_strategy as ns
def main():
    root = tk.Tk()
    root.withdraw()
    try:
        file_path = filedialog.askopenfilename()
        df = pd.read_excel(file_path)
    except Exception as e:
        messagebox.showerror("Error", f"Error reading file: {e}")
        return
    try:
        ns_report = ns.NegotiationStrategy(df)
        ns_report.generate_report()
    except Exception as e:
        messagebox.showerror("Error", f"Error generating report: {e}")
        return
if __name__ == "__main__":
    main()