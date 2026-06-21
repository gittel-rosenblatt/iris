import os
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
import datetime as dt 
import requests as rq

class IrisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Iris")
        self.root.geometry("1460x800")
        
        SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(SCRIPT_DIR, 'iris-icon.png')
        img_original = Image.open(logo_path).convert("RGBA")
        
        canvas_size = (256, 256)
        icon_size = (206, 206) 
        
        img_square = img_original.resize(icon_size, Image.Resampling.LANCZOS)
        
        mask = Image.new("L", icon_size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), icon_size], radius=36, fill=255)
        
        rounded_icon = Image.new("RGBA", icon_size)
        rounded_icon.paste(img_square, (0, 0), mask=mask)
        
        final_padded_canvas = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
        offset = ((canvas_size[0] - icon_size[0]) // 2, (canvas_size[1] - icon_size[1]) // 2)
        final_padded_canvas.paste(rounded_icon, offset)
        
        self.img = ImageTk.PhotoImage(final_padded_canvas)

        root.iconphoto(False, self.img)
        self.create_main_dashboard()
        
    def create_main_dashboard(self):
        self.root.columnconfigure(0, weight=1, uniform="group1")
        self.root.columnconfigure(1, weight=1, uniform="group1")
        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=1)
        self.root.rowconfigure(3, weight=1)

        titel = tk.Label(self.root, text="Iris: Lighting Up the Digital World", font=("Atkinson Hyperlegible", 70, "bold"),)
        titel.grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=5)

        self.close_btn = tk.Button(self.root, text="Close", font=("Atkinson Hyperlegible", 60, "bold"), command=self.root.destroy)
        self.close_btn.grid(row=0, column=1, sticky="ne", padx=10, pady=10)
 
        self.time_btn = tk.Button(self.root, text="Time", font=("Atkinson Hyperlegible", 108, "bold"), command=self.open_time_btn)
        self.time_btn.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.weather_btn = tk.Button(self.root, text="Weather", font=("Atkinson Hyperlegible", 108, "bold"), command=self.open_weather_btn)
        self.weather_btn.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        self.todo_btn = tk.Button(self.root, text="To Do", font=("Atkinson Hyperlegible", 108, "bold"), command=self.open_todo_btn)
        self.todo_btn.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        self.notes_btn = tk.Button(self.root, text="Notes", font=("Atkinson Hyperlegible", 108, "bold"), command=self.open_notes_btn)
        self.notes_btn.grid(row=2, column=1, sticky="nsew", padx=10, pady=10)

        self.email_btn = tk.Button(self.root, text="Email", font=("Atkinson Hyperlegible", 108, "bold"), command=self.open_email_btn)
        self.email_btn.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)

        self.forms_btn = tk.Button(self.root, text="Forms", font=("Atkinson Hyperlegible", 108, "bold"), command=self.open_forms_btn)
        self.forms_btn.grid(row=3, column=1, sticky="nsew", padx=10, pady=10)

    def open_time_btn(self):
        self.time_popup = tk.Toplevel(self.root)
        self.time_popup.title("Date & Time")
        self.time_popup.geometry("1410x750")
        center_frame = tk.Frame(self.time_popup)

        self.current_date = dt.datetime.now().strftime("%A, %B %d")
        date_label = tk.Label(center_frame, text=self.current_date, font=("Atkinson Hyperlegible", 90, "bold"))
        date_label.pack(pady=5)

        self.time_label = tk.Label(center_frame, text="", font=("Atkinson Hyperlegible", 90, "bold"))
        self.time_label.pack(pady=5)

        self.close_btn = tk.Button(self.time_popup, text="Close", font=("Atkinson Hyperlegible", 36, "bold"), command=self.time_popup.destroy)
        self.close_btn.place(relx=1.0, rely=0.0, anchor="ne")
        
        center_frame.pack(expand=True)

        def update_clock():
            self.current_time = dt.datetime.now().strftime("%I:%M %p")
            self.time_label.config(text=self.current_time)
            self.time_label.after(1000, update_clock)
        
        self.time_popup.grab_set()
        update_clock()

    def open_weather_btn(self):
        self.weather_popup = tk.Toplevel(self.root)
        self.weather_popup.title("Weather")
        self.weather_popup.geometry("1410x750")
        center_frame = tk.Frame(self.weather_popup)

        header_label = tk.Label(center_frame, text="Weather:", font=("Atkinson Hyperlegible", 90, "bold"))
        header_label.pack(pady=5)

        self.close_btn = tk.Button(self.weather_popup, text="Close", font=("Atkinson Hyperlegible", 36, "bold"), command=self.weather_popup.destroy)
        self.close_btn.place(relx=1.0, rely=0.0, anchor="ne")

        center_frame.pack(expand=True)

        def get_weather():
            ip_api = rq.get("http://ip-api.com/json/")

            if ip_api.status_code == 200:
                ip_data = ip_api.json()

                lon = ip_data.get("lon")
                lat = ip_data.get("lat")

                weather_api = rq.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,wind_direction_10m,wind_speed_10m,rain,showers&timezone=auto&wind_speed_unit=mph&temperature_unit=fahrenheit&precipitation_unit=inch")

                if weather_api.status_code == 200:
                    weather_data = weather_api.json()
                    
                    temp = weather_data["current"]["temperature_2m"]
                    humidity = weather_data["current"]["relative_humidity_2m"]
                    apparent_temp = weather_data["current"]["apparent_temperature"]
                    wind_direction = weather_data["current"]["wind_direction_10m"]
                    wind_speed = weather_data["current"]["wind_speed_10m"]
                    rain = weather_data["current"]["rain"]
                    shower = weather_data["current"]["showers"]
                    
                    return temp, humidity, apparent_temp, wind_direction, wind_speed, rain, shower

                else: 
                    print(f"Failed to fetch data. Error code: {weather_api.status_code}")
            else: 
                print(f"Failed to fetch data. Error code: {ip_api.status_code}")

        # The catcher sits on the left, the function execution sits on the right!
        temp, humidity, apparent_temp, wind_direction, wind_speed, rain, shower = get_weather()

        if wind_direction <= 22.5 or wind_direction > 337.5:
            direction = "north"
        elif wind_direction >= 22.5 and wind_direction < 67.5:
            direction = "northeast"
        elif wind_direction >= 67.5 and wind_direction < 112.5:
            direction = "east"
        elif wind_direction >= 112.5 and wind_direction < 157.5:
            direction = "southeast"
        elif wind_direction >= 157.5 and wind_direction < 202.5:
            direction = "south"
        elif wind_direction >= 202.5 and wind_direction < 247.5:
            direction = "southwest"
        elif wind_direction >= 247.5 and wind_direction < 292.5:
            direction = "west"
        elif wind_direction >= 292.5 and wind_direction < 337.5:
            direction = "northwest"

        weather_label = tk.Label(center_frame, text=f"""Temperature: {temp}°F
Humidity: {humidity}%
Feels Like: {apparent_temp}°F
Wind Direction: {wind_direction}° from the {direction}
Wind Speed: {wind_speed} miles per hour
Precipitation: {rain} inches of rain, 
{shower} inches of shower""", font=("Atkinson Hyperlegible", 70, "bold"))
        weather_label.pack(pady=5)

    def open_todo_btn(self):
        self.todo_popup = tk.Toplevel(self.root)
        self.todo_popup.title("To Do")
        self.todo_popup.geometry("1410x750")
        center_frame = tk.Frame(self.todo_popup)

        weather_label = tk.Label(center_frame, text="To Do loading...", font=("Atkinson Hyperlegible", 90, "bold"))
        weather_label.pack(pady=5)

        self.close_btn = tk.Button(self.todo_popup, text="Close", font=("Atkinson Hyperlegible", 36, "bold"), command=self.todo_popup.destroy)
        self.close_btn.place(relx=1.0, rely=0.0, anchor="ne")

        center_frame.pack(expand=True)

    def open_notes_btn(self):
        self.notes_popup = tk.Toplevel(self.root)
        self.notes_popup.title("Notes")
        self.notes_popup.geometry("1410x750")
        center_frame = tk.Frame(self.notes_popup)

        weather_label = tk.Label(center_frame, text="Notes loading...", font=("Atkinson Hyperlegible", 90, "bold"))
        weather_label.pack(pady=5)

        self.close_btn = tk.Button(self.notes_popup, text="Close", font=("Atkinson Hyperlegible", 36, "bold"), command=self.notes_popup.destroy)
        self.close_btn.place(relx=1.0, rely=0.0, anchor="ne")

        center_frame.pack(expand=True)

    def open_email_btn(self):
        self.email_popup = tk.Toplevel(self.root)
        self.email_popup.title("Email")
        self.email_popup.geometry("1410x750")
        center_frame = tk.Frame(self.email_popup)

        weather_label = tk.Label(center_frame, text="Email loading...", font=("Atkinson Hyperlegible", 90, "bold"))
        weather_label.pack(pady=5)

        self.close_btn = tk.Button(self.email_popup, text="Close", font=("Atkinson Hyperlegible", 36, "bold"), command=self.email_popup.destroy)
        self.close_btn.place(relx=1.0, rely=0.0, anchor="ne")

        center_frame.pack(expand=True)

    def open_forms_btn(self):
        self.forms_popup = tk.Toplevel(self.root)
        self.forms_popup.title("Forms")
        self.forms_popup.geometry("1410x750")
        center_frame = tk.Frame(self.forms_popup)

        weather_label = tk.Label(center_frame, text="Forms loading...", font=("Atkinson Hyperlegible", 90, "bold"))
        weather_label.pack(pady=5)

        self.close_btn = tk.Button(self.forms_popup, text="Close", font=("Atkinson Hyperlegible", 36, "bold"), command=self.forms_popup.destroy)
        self.close_btn.place(relx=1.0, rely=0.0, anchor="ne")

        center_frame.pack(expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = IrisApp(root)
    root.mainloop()