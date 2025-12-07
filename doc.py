import tkinter as tk
import ctypes
import time
import threading

# Make UI sharp on Windows
ctypes.windll.shcore.SetProcessDpiAwareness(1)

# Efficiency Data
efficiency_data = [
    ("Tuberculosis", "86%", "74%"),
    ("Pneumonia", "89%", "94%"),
    ("Cardiovascular diseases", "54%", "23%"),
    ("Diabetes", "42%", "45%"),
    ("COPD", "54%", "60%")
]

# Spinner state and helpers for analysing animation
spinner_chars = ["|", "/", "-", "\\"]
spinner_index = 0
spinner_job = None

def _spin_once():
    """Internal: advance spinner and schedule next tick."""
    global spinner_index, spinner_job
    # Update the result label with spinner char
    result_label.config(text=f"Analysing... {spinner_chars[spinner_index]}", fg="#0078D4")
    spinner_index = (spinner_index + 1) % len(spinner_chars)
    spinner_job = root.after(150, _spin_once)

def start_spinner():
    """Start the spinner if not already running."""
    global spinner_job
    if spinner_job is None:
        _spin_once()

def stop_spinner():
    """Stop the spinner if running."""
    global spinner_job
    if spinner_job is not None:
        try:
            root.after_cancel(spinner_job)
        except Exception:
            pass
        spinner_job = None

def analyse_doctor():
    reg_no = entry.get().strip()

    if reg_no == "":
        stop_spinner()
        result_label.config(text="Please enter a registration number.", fg="red")
        doctor_info_label.config(text="")
        return

    # Show doctor name and the entered registration number
    doctor_info_label.config(text=f"Doctor: Dr. Aditya Garg    Reg No: {reg_no}", fg="black")

    # Start spinner animation and run analysis in background
    start_spinner()

    # Run the wait in a thread so GUI doesn't freeze
    def wait_and_display():
        time.sleep(5)  # 5 seconds analysing

        output = "Disease                         National %       Doctor %\n"
        output += "-"*60 + "\n"
        for d, n, doc in efficiency_data:
            output += f"{d:<30} {n:<15} {doc}\n"

        # Schedule GUI update on main thread: stop spinner and display output
        def display_output():
            stop_spinner()
            result_label.config(text=output, fg="black", justify="left", font=("Consolas", 12))

        root.after(0, display_output)

    threading.Thread(target=wait_and_display).start()


# ----------------- GUI Setup -----------------
root = tk.Tk()
root.title("Doctor Efficiency Analysis")
root.geometry("1920x1080")
root.resizable(False, False)

title = tk.Label(root, text="Doctor Efficiency Checker", font=("Segoe UI", 20))
title.pack(pady=10)

frame = tk.Frame(root)
frame.pack(pady=10)

# Doctor info label (updated when analysing)
doctor_info_label = tk.Label(root, text="", font=("Segoe UI", 14))
doctor_info_label.pack(pady=6)

label = tk.Label(frame, text="Please enter the Doctor's Registration Number:", font=("Segoe UI", 14))
label.grid(row=0, column=0, padx=5)

entry = tk.Entry(frame, font=("Segoe UI", 14), width=20)
entry.grid(row=0, column=1, padx=5)

analyse_btn = tk.Button(root, text="Analyse", font=("Segoe UI", 16), command=analyse_doctor)
analyse_btn.pack(pady=10)

result_label = tk.Label(root, text="", font=("Segoe UI", 16))
result_label.pack(pady=20)

root.mainloop()
