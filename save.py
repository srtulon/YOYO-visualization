from PIL import Image
import os

def make_pdf():
    image_files = [f for f in os.listdir() if f.endswith(".png")]
    image_files = sorted(image_files, key=lambda x: int(os.path.splitext(x)[0]))
    photo_images = []
    for image_file in image_files:
        img = Image.open(image_file)
        photo_img = img.convert('RGB')
        photo_images.append(photo_img)
    
    format = input("Do you want GIF or PDF or both? : ")
    name = input("Please enter name of the file (default name \"yoyo\") : ")
    if name == '':
        name = 'yoyo'
    if format.lower() == 'pdf':
        photo_images[0].save(name+'.pdf', save_all=True, append_images=photo_images[1:])
        print("File saved as "+name+'.pdf')
    elif format.lower() == 'gif':
        photo_images[0].save(name+'.gif', save_all=True, append_images=photo_images[1:],duration=1000, loop=0)
        print("File saved as "+name+'.gif')
    elif format.lower() == 'both':
        photo_images[0].save(name+'.pdf', save_all=True, append_images=photo_images[1:])
        print("File saved as "+name+'.pdf')
        photo_images[0].save(name+'.gif', save_all=True, append_images=photo_images[1:],duration=1000, loop=0)
        print("File saved as "+name+'.gif')


make_pdf()