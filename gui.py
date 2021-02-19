from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
from cv2 import imread, imwrite
import numpy as np
from scipy.io.wavfile import read, write
import imghdr, sndhdr


window = Tk()
window.resizable(0,0)

def browse():
    filename.delete(0, END)
    path = askopenfilename(title='Open File')
    if len(path) > 0:
        filename.insert(END, path)
    else:
        filename.insert(END, '')


def save():
    ftypes = [('All file types', '*.*'), ('wav audio file', '*.wav'), ('JPEG format', '*.jpg')]
    path = asksaveasfilename(title='Save As', confirmoverwrite=True, filetypes=ftypes)
    if len(path) != 0:
        return path


def encrypt():
    message.delete(0.0, END)
    img_formats = ['rgb', 'gif', 'pbm', 'pgm', 'ppm', 'tiff', 'rast', 'xbm', 'jpeg', 'jpg', 'bmp', 'png', 'webp', 'exr']
    
    file_path = file.get()
    try:
        format = imghdr.what(file_path)
    except:
        raise Exception(message.insert(END, 'File not found'))
        
    if format not in img_formats:
        raise Exception(message.insert(END, 'The file to be encrypted is not an image'))

    img = imread(file_path)
    
    height, width, channel = img.shape
        
    channel = np.uint8(channel)

    height = str(height)
    h1 = np.uint8(height[:2])
    h2 = np.uint8(height[2:])

    width = str(width)
    w1 = np.uint8(width[:2])
    w2 = np.uint8(width[2:])

    img_data = np.ravel(img)

    img_data = np.append(img_data, [h1, h2, w1, w2, channel])
    
    target_path = save()
    if target_path is not None:
        write(f"{target_path}.wav", 48000, img_data)
        message.insert(END, 'Encrypted Successfully')
    else:
        message.insert(END, 'Where to save?')
def decrypt():
    message.delete(0.0, END)
    file_path = file.get()
    try:
        format = sndhdr.what(file_path)
    except FileNotFoundError:
        raise Exception(message.insert(END, 'File not found'))
    if format is None:
        raise Exception(message.insert(END, 'This is not a wav audio file'))
    
    try:
        fs, aud_data = read(file_path)
        
        channel = aud_data[-1]
        w2 = aud_data[-2]
        w1 = aud_data[-3]
        h2 = aud_data[-4]
        h1 = aud_data[-5]
        

        height = int(str(h1) + str(h2))
        width = int(str(w1) + str(w2)) 

        aud_data = np.delete(aud_data, np.s_[-5:])  # s_[a:b] returns a tuple containing numbers from a to b(excluded) 

        img_data = np.reshape(aud_data, (height, width, channel))
        target_path = save()
        if target_path is not None:
            img = imwrite(f'{target_path}.jpg', img_data)
            message.insert(END, 'Decrypted Successfully')
        else:
            message.insert(END, 'Where to save?')
    except Exception:
        message.insert(END, 'The audio does not contain image')



window.title("Encrypt image in audio")

l1 = Label(window, text="file path")
l1.grid(row=0, column=0)

file = StringVar()
filename = Entry(window, textvariable=file, width=80)
filename.grid(row=1, column=0, padx=10, pady=10)

l2 = Label(window, text="success/error message")
l2.grid(row=2, column=0)
message = Text(window, height=4, width=60, fg='red')
message.grid(row=3, rowspan=2, column=0)


info = Label(window,
text='''This Encryption software is developed by
Sarmad Rafique and Yasir Ali
Copyright © 2021. All rights reserved.
''', font=20, fg='green')
info.grid(row=5, column=0)

## buttons
btn_browse = Button(window, text="Browse", width=12, command=browse)
btn_browse.grid(row=1, column=2, padx=10)

btn_encrypt = Button(window, text="Encrypt", width=12, command=encrypt)
btn_encrypt.grid(row=3, column=2)

btn_decrypt = Button(window, text="Decrypt", width=12, command=decrypt)
btn_decrypt.grid(row=4, column=2)

btn_close = Button(window, text="Close", width=12, command=window.destroy)
btn_close.grid(row=5, column=2)

window.mainloop()