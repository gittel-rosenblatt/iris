import os
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk

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
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=1)

        self.time_btn = tk.Button(self.root, text="Time", font=("Atkinson Hyperlegible", 36, "bold"))
        self.time_btn.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.weather_btn = tk.Button(self.root, text="Weather", font=("Atkinson Hyperlegible", 36, "bold"))
        self.weather_btn.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.todo_btn = tk.Button(self.root, text="To Do", font=("Atkinson Hyperlegible", 36, "bold"))
        self.todo_btn.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.notes_btn = tk.Button(self.root, text="Notes", font=("Atkinson Hyperlegible", 36, "bold"))
        self.notes_btn.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        self.email_btn = tk.Button(self.root, text="Email", font=("Atkinson Hyperlegible", 36, "bold"))
        self.email_btn.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        self.forms_btn = tk.Button(self.root, text="Forms", font=("Atkinson Hyperlegible", 36, "bold"))
        self.forms_btn.grid(row=2, column=1, sticky="nsew", padx=10, pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = IrisApp(root)
    root.mainloop()