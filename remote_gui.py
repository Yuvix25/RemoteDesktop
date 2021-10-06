import threading
from tkinter import *
from PIL import ImageTk, Image
import numpy as np
import cv2

class GUI:
    def __init__(self, resolution, is_controlled, stream):
        self.res = resolution
        self.isctrld = is_controlled
        self.root = TkRoot(stream)
        self.panel = None
    
    def show_img(self, image):
        image = ImageTk.PhotoImage(Image.fromarray(image))
		
        # if the panel is not None, we need to initialize it
        if self.panel is None:
            self.panel = Label(image=image)
            self.panel.image = image
            self.panel.pack(side="left", padx=10, pady=10)

        # otherwise, simply update the panel
        else:
            self.panel.configure(image=image)
            self.panel.image = image
    

    def stream_loop(self, data):
        def loop():
            while True:
                img = next(data)
                img = np.fromstring(img, dtype=np.uint8)
                img = cv2.imdecode(img, 1)
                self.show_img(img)
        
        t = threading.Thread(target=loop)
        t.start()
        self.root.tk.mainloop()


class TkRoot:
    def __init__(self, stream):
        self.tk = Tk()
        self.stream = stream
        self.tk.bind("<KeyPress>", self.onKeyPress)

    def onKeyPress(self, event):
        print(event)