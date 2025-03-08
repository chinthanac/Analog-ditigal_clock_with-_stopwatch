import tkinter as tk
from tkinter import Label, Listbox, ttk, Canvas, Entry, messagebox
import time
import math
import winsound
import os  

class StopwatchClock:
    def __init__(self, root):
        self.root = root
        self.root.title("Stopwatch & Clock")
        self.root.geometry("400x550")
        self.root.configure(bg="#2C3E50")
        
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 12), padding=5)
        style.configure("TLabel", font=("Arial", 20), background="#2C3E50", foreground="white")
        
        self.canvas = Canvas(root, width=200, height=200, bg="#2C3E50", highlightthickness=0)
        self.canvas.pack(pady=10)
        
        self.time_label = Label(root, text="00:00:00", font=("Arial", 24), bg="#2C3E50", fg="white")
        self.time_label.pack(pady=10)
        
        self.stopwatch_label = Label(root, text="00:00:00.000", font=("Arial", 24), bg="#2C3E50", fg="#E74C3C")
        self.stopwatch_label.pack(pady=10)
        
        self.alert_label = Label(root, text="Set Alert Time (HH:MM:SS):", font=("Arial", 12), bg="#2C3E50", fg="white")
        self.alert_label.pack()
        
        self.alert_entry = Entry(root, font=("Arial", 14), width=10, justify="center")
        self.alert_entry.pack(pady=5)
        self.alert_entry.insert(0, "00:00:05")  # Default alert time
        
        button_frame = tk.Frame(root, bg="#2C3E50")
        button_frame.pack(pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_stopwatch)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_stopwatch)
        self.stop_button.grid(row=0, column=1, padx=5)
        
        self.reset_button = ttk.Button(button_frame, text="Reset", command=self.reset_stopwatch)
        self.reset_button.grid(row=0, column=2, padx=5)
        
        self.lap_button = ttk.Button(button_frame, text="Lap", command=self.record_lap)
        self.lap_button.grid(row=0, column=3, padx=5)
        
        self.lap_listbox = Listbox(root, height=5, font=("Arial", 12), bg="#ECF0F1", fg="black")
        self.lap_listbox.pack(pady=10, fill="x", padx=20)
        
        self.running = False
        self.start_time = 0
        self.elapsed_time = 0
        
        self.last_hour = None
        self.update_clock()
        self.update_analog_clock()
        self.load_laps()  # Load saved lap times when app starts

    def update_clock(self):
        current_time = time.strftime("%H:%M:%S")
        self.time_label.config(text=current_time)
        
        current_hour = time.strftime("%H")
        if self.last_hour is None or self.last_hour != current_hour:
            self.last_hour = current_hour
            self.play_sound()
            messagebox.showinfo("Hourly Alert", "It's a new hour: " + current_time)
        
        self.root.after(1000, self.update_clock)
    
    def update_analog_clock(self):
        self.canvas.delete("all")
        width, height = 200, 200
        center_x, center_y = width // 2, height // 2
        radius = 80
        
        self.canvas.create_oval(center_x - radius, center_y - radius, center_x + radius, center_y + radius, outline="white", width=2)
        
        current_time = time.localtime()
        
        for angle, length, width in [(current_time.tm_hour % 12 * 30, 40, 6), (current_time.tm_min * 6, 60, 4), (current_time.tm_sec * 6, 70, 2)]:
            angle = math.radians(angle - 90)
            x = center_x + length * math.cos(angle)
            y = center_y + length * math.sin(angle)
            self.canvas.create_line(center_x, center_y, x, y, fill="white", width=width)
        
        self.root.after(1000, self.update_analog_clock)
    
    def update_stopwatch(self):
        if self.running:
            self.elapsed_time = time.time() - self.start_time
            minutes, seconds = divmod(int(self.elapsed_time), 60)
            hours, minutes = divmod(minutes, 60)
            milliseconds = int((self.elapsed_time - int(self.elapsed_time)) * 1000)
            self.stopwatch_label.config(text=f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}")
            
            if self.check_alert():
                self.play_sound()
                messagebox.showinfo("Stopwatch Alert", "Stopwatch reached the alert time!")
            
            self.root.after(10, self.update_stopwatch)
    
    def start_stopwatch(self):
        if not self.running:
            self.running = True
            self.start_time = time.time() - self.elapsed_time
            self.update_stopwatch()
    
    def stop_stopwatch(self):
        if self.running:
            self.running = False
    
    def reset_stopwatch(self):
        self.running = False
        self.elapsed_time = 0
        self.stopwatch_label.config(text="00:00:00.000")
        self.lap_listbox.delete(0, tk.END)

        # Clear saved lap file
        open("lap.txt", "w").close()

    def record_lap(self):
        if self.running:
            minutes, seconds = divmod(int(self.elapsed_time), 60)
            hours, minutes = divmod(minutes, 60)
            milliseconds = int((self.elapsed_time - int(self.elapsed_time)) * 1000)
            lap_time = f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"
            self.lap_listbox.insert(tk.END, lap_time)

            # Append the lap time to lap.txt
            with open("lap.txt", "a") as file:
                file.write(lap_time + "\n")

    def check_alert(self):
        alert_time = self.alert_entry.get()
        try:
            h, m, s = map(int, alert_time.split(":"))
            alert_seconds = h * 3600 + m * 60 + s
            return int(self.elapsed_time) == alert_seconds
        except ValueError:
            return False
    
    def play_sound(self):
        winsound.Beep(1000, 500)

    def load_laps(self):
        """Load previously saved lap times into the listbox."""
        if os.path.exists("lap.txt") and os.stat("lap.txt").st_size > 0:
            with open("lap.txt", "r") as file:
                for lap in file:
                    self.lap_listbox.insert(tk.END, lap.strip())

if __name__ == "__main__":
    root = tk.Tk()
    app = StopwatchClock(root)
    root.mainloop()
