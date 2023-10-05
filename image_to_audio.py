# importing modules
from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
from cv2 import imread, imwrite
import numpy as np
from scipy.io.wavfile import read, write
import imghdr, sndhdr                          # image header and sound header


# creating an instance of tkinter gui window
window = Tk()
window.resizable(0,0)  # to disbale maximization of window

# function for `browse` button
def browse():
    filename.delete(0, END)                    # empty the `filename` entry when browse button is pressed
    path = askopenfilename(title='Open File')  # accessing the OS buit-in 'browse' interface and storing the pathname in `path` variable
    if len(path) > 0:                          # if a file is selected
        filename.insert(END, path)             # insert it in the filename entry
    else:                                      # if no file is selected
        filename.insert(END, '')               # insert an empty string in `filename` entry


# for saving the encrypted and/or decrypted files
def save():
    ftypes = [('All file types', '*.*'), ('wav audio file', '*.wav'), ('JPEG format', '*.jpg')]
    path = asksaveasfilename(title='Save As', confirmoverwrite=True, filetypes=ftypes)  # accesing the OS buit-in 'save as' interface
    if len(path) != 0:
        return path


# encryption function for the `encrypt` button
def encrypt():
    message.delete(0.0, END)            # empty the `message` Text widget
    img_formats = ['rgb', 'gif', 'pbm', 'pgm', 'ppm', 'tiff', 'rast', 'xbm', 'jpeg', 'jpg', 'bmp', 'png', 'webp', 'exr']
    
    file_path = filename.get()          # get the path of the file from the `filename` entry
    try:
        format = imghdr.what(file_path) # check the format of the input file and see if it is an image
    except:
        raise Exception(message.insert(END, 'File not found')) 
        
    if format not in img_formats:       # if the input file is not in the specified `img_formats` list
        raise Exception(message.insert(END, 'The file to be encrypted is not an image'))

    img = imread(file_path)             # read the image through cv2 function `imread`
    
    height, width, channel = img.shape  # get the shape of the image
        
    channel = np.uint8(channel)         # convert the `channel` int to unsigned 8-bit integer

    height = str(height)                # convert the `height` integer into string
    h = []                              # list for storing the ascii of each digit
    for char in height:                 # loop over each digit
        asci = np.uint8(ord(char))      # convert the digit to its ascii value
        h.append(asci)                  
    len_h = np.uint8(len(h))
    h.append(len_h)

    width = str(width)                  # do the same steps to `width`
    w = []
    for char in width:
        asci = np.uint8(ord(char))
        w.append(asci)
    len_w = np.uint8(len(w))
    w.append(len_w)

    passphrase = passwd.get()                     # get the entered passphrase from the `passwd` entry
    len_pass = np.uint8(len(passphrase))          # take the length of the passphrase and convert it into uint8
    char_pass = []
    for char in passphrase:                       # parse each  character of the passphrase
        char_pass.append(np.uint8(ord(char)))     # convert each character to it's ascii and then to uint8 and append it to a list
    char_pass.append(len_pass)                    # append the `len_pass` to the list as well

    img_data = np.ravel(img)                # convert the n-dimensional image samples array to 1-dimensional array

    img_data = np.append(img_data, h)
    img_data = np.append(img_data, w)
    img_data = np.append(img_data, channel)
    img_data = np.append(img_data, char_pass)                             # append the `char_pass`
    img_data = np.append(img_data, [np.uint8(100) for i in range(10)])    # append 10 values each of value 100, so  that at decryption, we know that the audio conatins an image

    target_path = save()              # get the target path from the `save` function
    if target_path is not None:                          # if a path is selected
        write(f"{target_path}.wav", 48000, img_data)     # write the `img_data` array to wav audio signal with fs=48000
        message.insert(END, 'Encrypted Successfully')    # to show that operation is done successully
    else:
        message.insert(END, 'Where to save?\nClick the button again')
    
    passwd.delete(0, END)           # empty the `passwd` entry when the encryption is done


# decryption function for the `decrypt` button
def decrypt():
    message.delete(0.0, END)                # empty the `message` Text widget
    file_path = filename.get()              # get the path of the file from the `filename` entry
    try:
        format = sndhdr.what(file_path)     # check the format of the input file and see if it is audio file
    except FileNotFoundError:
        raise Exception(message.insert(END, 'File not found'))
    if format is None:
        raise Exception(message.insert(END, 'This is not a wav audio file'))
    
    try:
        wrong_pass = False                     # assuming that the entered password is not wrong
        valid_image = True                     # assuming that the audio signal contains a valid image

        fs, aud_data = read(file_path)          # read the audio signal. `fs` is the sampling freq and `aud_data` are the audio samples
        
        for i in range(10):                     # check for 10 consecutive values each of value 100 to check if audio is the output of our program
            if aud_data[-1] != 100:             # if the sample is not 100
                valid_image = False
                raise Exception(message.insert(END, "The audio does not contain a valid image"))
            aud_data = np.delete(aud_data, -1)       # delete the sample if it is 100 and loop over again
        
        #### if the audio satifies the above criteria then proceed further ###

        len_pass = aud_data[-1]                 # get the length of password that was appended during encryption
        aud_data = np.delete(aud_data, -1)      # then delete that sample
        passphrase = passwd.get()               # get the passphrase from the `passwd` entry which will be used to verify the password given at encryption

        if (len_pass == 0 and len(passphrase) != 0) or (len_pass != 0 and len(passphrase) == 0):
            wrong_pass = True
            raise Exception(message.insert(END, "Wrong password"))

        passphrase = passphrase[::-1]               # reverse the `passphrase` string
        for i in range(len_pass):                   # loop over the samples to verify the passphrase
            if aud_data[-1] != ord(passphrase[i]):  # if ascii of a character of passphrase is not equal to the original password
                wrong_pass =True
                raise Exception(message.insert(END, "Wrong password"))   # stop the decryption with the error, "Wrong password"
            aud_data = np.delete(aud_data, -1)      # delete the sample if it is equal to the corresponding ascii of the character of passphrase

        ### retrieve the channel, height and width data ###
        channel = aud_data[-1]
        aud_data = np.delete(aud_data, -1)

        len_w = aud_data[-1]                   # number of digits in width of image
        aud_data = np.delete(aud_data, -1)
        width = ""
        for i in range(len_w):
            digit = chr(aud_data[-1])          # convert the ascii value to digit
            width += digit
            aud_data = np.delete(aud_data, -1)
        width = int(width[::-1])               # reverse the string and convert it into int

        len_h = aud_data[-1]
        aud_data = np.delete(aud_data, -1)
        height = ""
        for i in range(len_h):
            digit = chr(aud_data[-1])
            height += digit
            aud_data = np.delete(aud_data, -1)
        height = int(height[::-1])

        img_data = np.reshape(aud_data, (height, width, channel))   # reshape the 1-dimensional audio signal array to n-dimensional array according to the `height`, `width` and `channel`
        target_path = save()                               # get the target path from the `save` function
        if target_path is not None:                        # if a path is selected
            img = imwrite(f'{target_path}.jpg', img_data)  # write the `img_data` array to jpg image signal
            message.insert(END, 'Decrypted Successfully')  # to show that decryption is successful
        else:
            message.insert(END, 'Where to save?\nClick the button again')
    
    except Exception:
        if valid_image and not wrong_pass:               # We put this extra if statement to avoid the exception being raised twice. i.e if the Exception for 'audio does not contain a valid image' or 'Wrong password' or both has been raised in the above `try` block then we don't need this Exception to be raised
            raise Exception(message.insert(END, "The audio does not contain a valid image"))

    passwd.delete(0, END)


window.wm_title("Encrypt image in audio (DSP mini Project)")   # set the title of the window

l1 = Label(window, text="file path")                           # create Label widget
l1.grid(row=0, column=0)                                       # place it at row=0 and column=0

file = StringVar()                                             # value holder for filename
filename = Entry(window, textvariable=file, width=80)          # create Entry widget `filename`
filename.grid(row=1, column=0, padx=10, pady=10)

l2 = Label(window, text="Enter password")                      # create Label widget
l2.grid(row=2, column=0)
password = StringVar()                                         # value holder for password
passwd = Entry(window, textvariable=password, width=80)        # create Entry widget for password
passwd.grid(row=3, column=0)

l2 = Label(window, text="success/error message")               # Label widget
l2.grid(row=4, column=0)
message = Text(window, height=4, width=60, fg='red')           # Entry widget for showing error/success messages
message.grid(row=5, rowspan=2, column=0)


info = Label(window,                                          # Label widget for showing the program authors' info
text='''This Encryption software is developed by 
Yasir Ali (17PWELE5094) and Sarmad Rafique (17PWELE5105)
Copyright © 2021. All rights reserved.
''', font=20, fg='green')
info.grid(row=7, column=0)

### buttons ###
btn_browse = Button(window, text="Browse", width=12, command=browse)        # Browse Button
btn_browse.grid(row=1, column=2, padx=10)

btn_encrypt = Button(window, text="Encrypt", width=12, command=encrypt)     # Encrypt Button
btn_encrypt.grid(row=3, column=2)

btn_decrypt = Button(window, text="Decrypt", width=12, command=decrypt)     # Decrypt Button
btn_decrypt.grid(row=5, column=2)

btn_close = Button(window, text="Close", width=12, command=window.destroy)  # Close Button
btn_close.grid(row=7, column=2)

window.mainloop()           # end of `window` instance
