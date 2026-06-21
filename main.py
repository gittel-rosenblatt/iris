import os
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk

class IrisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Iris")
        self.root.geometry("1460x800")
        
        SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(SCRIPT_DIR, 'iris-logo.png')
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
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = IrisApp(root)
    root.mainloop()