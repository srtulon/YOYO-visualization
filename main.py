import subprocess
import os

def process():
    # Run the main code
    subprocess.run(["python", "yoyo.py"])

    option = input('Do you want the result as animation, saved file or both? Press enter for animation (animation,save,both): ')
    
    while option.lower() not in ['animation', '', 'save', 'both']:
        option = input('Please input animation, pdf or both : ')

    if option.lower() == 'animation' or option.lower() == '':
        subprocess.run(["python", "animation.py"])
    
    elif option.lower() == 'save':
        subprocess.run(["python", "save.py"])
        
    elif option.lower() == 'both':
        subprocess.run(["python", "animation.py"])
        subprocess.run(["python", "save.py"])

    image_files = [f for f in os.listdir() if f.endswith(".png")]
    for image in image_files:
        os.remove(image) 

process()

while True:
    prompt = input('Do you want to do it again? (yes/no) : ')
    if prompt.lower() == 'yes' or prompt.lower() == 'y' or prompt.lower() == '':
        process()
    else:
        break