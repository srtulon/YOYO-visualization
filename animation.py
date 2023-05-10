# import required modules
import tkinter as tk
from PIL import Image, ImageTk
import os

delay = float(input('Please enter the animation delay in second : '))

x = 0
def show_slide():
    root = tk.Tk()
    root.geometry("640x480")

    image_files = [f for f in os.listdir() if f.endswith(".png")]
    image_files = sorted(image_files, key=lambda x: int(os.path.splitext(x)[0]))
    photo_images = []

    for image_file in image_files:
        img = Image.open(image_file)
        photo_img = ImageTk.PhotoImage(img)
        photo_images.append(photo_img)


    def move():
        global x
        if x < len(photo_images):
            l.config(image=photo_images[x])
            x = (x + 1)
            root.after(int(delay*1000), move)
        else:
            root.destroy()

    l = tk.Label(root)
    l.grid(row=0, column=0)

    move()
    root.mainloop()


show_slide()