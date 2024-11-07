import customtkinter as ctk
import psutil
import time
from threading import Thread

class MTech_System_Monitor(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("MTech Monitor")
        self.geometry("400x500")
        self.grid_columnconfigure(0, weight=1)
        
        # Theme settings
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Title label
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="System Monitor",
            font=("Helvetica", 20, "bold")
        )
        self.title_label.grid(row=0, column=0, pady=10)
        
        # Temperature frame
        self.temp_frame = ctk.CTkFrame(self.main_frame)
        self.temp_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # CPU Temperature label
        self.cpu_temp_label = ctk.CTkLabel(
            self.temp_frame,
            text="CPU Temperature: N/A",
            font=("Helvetica", 14)
        )
        self.cpu_temp_label.grid(row=0, column=0, padx=10, pady=10)
        
        # CPU Usage Progress Bar
        self.cpu_progress = ctk.CTkProgressBar(
            self.temp_frame,
            width=300,
            height=20,
            border_width=2,
            progress_color="green"
        )
        self.cpu_progress.grid(row=1, column=0, padx=10, pady=5)
        self.cpu_progress.set(0)
        
        # CPU Usage label
        self.cpu_usage_label = ctk.CTkLabel(
            self.temp_frame,
            text="CPU Usage: 0%",
            font=("Helvetica", 14)
        )
        self.cpu_usage_label.grid(row=2, column=0, padx=10, pady=5)
        
        # Memory Usage frame
        self.memory_frame = ctk.CTkFrame(self.main_frame)
        self.memory_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        
        # Memory Usage label
        self.memory_label = ctk.CTkLabel(
            self.memory_frame,
            text="Memory Usage: N/A",
            font=("Helvetica", 14)
        )
        self.memory_label.grid(row=0, column=0, padx=10, pady=10)
        
        # Memory Progress Bar
        self.memory_progress = ctk.CTkProgressBar(
            self.memory_frame,
            width=300,
            height=20,
            border_width=2,
            progress_color="blue"
        )
        self.memory_progress.grid(row=1, column=0, padx=10, pady=5)
        self.memory_progress.set(0)
        
        # Refresh rate slider
        self.refresh_label = ctk.CTkLabel(
            self.main_frame,
            text="Refresh Rate (seconds)",
            font=("Helvetica", 12)
        )
        self.refresh_label.grid(row=3, column=0, pady=(20, 0))
        
        self.refresh_slider = ctk.CTkSlider(
            self.main_frame,
            from_=0.1,
            to=5.0,
            number_of_steps=49
        )
        self.refresh_slider.grid(row=4, column=0, pady=10)
        self.refresh_slider.set(1.0)
        
        # Start monitoring thread
        self.running = True
        self.monitor_thread = Thread(target=self.update_stats, daemon=True)
        self.monitor_thread.start()

    def get_cpu_temperature(self):
        try:
            temps = psutil.sensors_temperatures()
            if 'coretemp' in temps:
                return sum(temp.current for temp in temps['coretemp']) / len(temps['coretemp'])
            elif 'cpu_thermal' in temps:  # For Raspberry Pi
                return temps['cpu_thermal'][0].current
            return None
        except:
            return None

    def update_stats(self):
        while self.running:
            # Get CPU temperature
            cpu_temp = self.get_cpu_temperature()
            if cpu_temp is not None:
                self.cpu_temp_label.configure(
                    text=f"CPU Temperature: {cpu_temp:.1f}°C"
                )
            
            # Get CPU usage
            cpu_percent = psutil.cpu_percent()
            self.cpu_progress.set(cpu_percent / 100)
            self.cpu_usage_label.configure(text=f"CPU Usage: {cpu_percent}%")
            
            # Get memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            self.memory_progress.set(memory_percent / 100)
            self.memory_label.configure(
                text=f"Memory Usage: {memory_percent:.1f}% "
                f"({memory.used // 1024 // 1024}MB / {memory.total // 1024 // 1024}MB)"
            )
            
            # Update progress bar colors based on usage
            self.cpu_progress.configure(
                progress_color="green" if cpu_percent < 60 
                else "orange" if cpu_percent < 85 
                else "red"
            )
            
            self.memory_progress.configure(
                progress_color="blue" if memory_percent < 60 
                else "orange" if memory_percent < 85 
                else "red"
            )
            
            # Get refresh rate from slider
            refresh_rate = self.refresh_slider.get()
            time.sleep(refresh_rate)

    def on_closing(self):
        self.running = False
        self.monitor_thread.join(timeout=1)
        self.destroy()

if __name__ == "__main__":
    app = MTech_System_Monitor()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()