import numpy as np
import cv2
import tkinter as tk
from threading import Thread
from time import sleep
from copy import deepcopy

class Controller(tk.Frame):
    def __init__(self, parent, manual_override, amplitude=60):
        self.parent = parent
        self.amplitude = amplitude
        # self.frame = tk.Frame(self, parent, bg='#81ecec')
        tk.Frame.__init__(self, parent, bg='#81ecec')
        self.chosen = None
        # create a prompt, an input box, an output label,
        # and a button to do the computation
        # self.prompt = tk.Label(self, text="Choose the name:",
        #                        anchor="w",
        #                        font=('Ubuntu Mono',15), 
        #                        fg='#000000',
        #                        bg='#81ecec',)
        self.manual_override = manual_override
        self.buttons = {}
        self.var = tk.IntVar()
        self.buttons['manual_override'] = tk.Checkbutton(self, text='Override', 
                                        font=('Ubuntu Mono',20), 
                                        bg='#00b894',
                                        activebackground='#0dd8b0',
                                        variable=self.var,
                                        command=self.click_check
                                        )
        self.buttons['panLeft'] = tk.Button(self, text='L', 
                                        font=('Ubuntu Mono',20), 
                                        bg='#00b894',
                                        activebackground='#0dd8b0',
                                        height=1,
                                        width=2,
                                        )
        
        self.buttons['panRight'] = tk.Button(self, text='R', 
                                        font=('Ubuntu Mono',20), 
                                        bg='#00b894',
                                        activebackground='#0dd8b0',
                                        height=1,
                                        width=2,
                                        )

        self.buttons['tiltUp'] = tk.Button(self, text='U', 
                                        font=('Ubuntu Mono',20), 
                                        bg='#00b894',
                                        activebackground='#0dd8b0',
                                        height=1,
                                        width=2,
                                        )

        self.buttons['tiltDown'] = tk.Button(self, text='D', 
                                        font=('Ubuntu Mono',20), 
                                        bg='#00b894',
                                        activebackground='#0dd8b0',
                                        height=1,
                                        width=2,
                                        )
        self.buttons['zoomIn'] = tk.Button(self, text='+', 
                                        font=('Ubuntu Mono',20), 
                                        bg='#00b894',
                                        activebackground='#0dd8b0',
                                        height=1,
                                        width=1,
                                        )
        self.buttons['zoomOut'] = tk.Button(self, text='-', 
                                        font=('Ubuntu Mono',20), 
                                        bg='#00b894',
                                        activebackground='#0dd8b0',
                                        height=1,
                                        width=1,
                                        )

        global_pady = 20
        global_padx = 20
        self.buttons['manual_override'].pack()
        self.buttons['tiltUp'].pack(side= tk.TOP )
        self.buttons['tiltDown'].pack(side= tk.BOTTOM )
        self.buttons['panLeft'].pack(side= tk.LEFT )
        self.buttons['panRight'].pack(side= tk.RIGHT )
        self.buttons['zoomOut'].pack(side= tk.BOTTOM )
        self.buttons['zoomIn'].pack(side= tk.BOTTOM )

        # for button in self.buttons:
        #     self.buttons[button].pack(side="top", fill="x", pady=global_pady, padx=global_padx)

        self.buttons['panLeft'].bind('<ButtonPress-1>', lambda event, action='left': self.choose(action))
        self.buttons['panLeft'].bind('<ButtonRelease-1>', lambda event, action=None: self.choose(action))

        self.buttons['panRight'].bind('<ButtonPress-1>', lambda event, action='right': self.choose(action))
        self.buttons['panRight'].bind('<ButtonRelease-1>', lambda event, action=None: self.choose(action))

        self.buttons['tiltUp'].bind('<ButtonPress-1>', lambda event, action='up': self.choose(action))
        self.buttons['tiltUp'].bind('<ButtonRelease-1>', lambda event, action=None: self.choose(action))

        self.buttons['tiltDown'].bind('<ButtonPress-1>', lambda event, action='down': self.choose(action))
        self.buttons['tiltDown'].bind('<ButtonRelease-1>', lambda event, action=None: self.choose(action))

        self.buttons['zoomIn'].bind('<ButtonPress-1>', lambda event, action='zoomIn': self.choose(action))
        self.buttons['zoomIn'].bind('<ButtonRelease-1>', lambda event, action=None: self.choose(action))

        self.buttons['zoomOut'].bind('<ButtonPress-1>', lambda event, action='zoomOut': self.choose(action))
        self.buttons['zoomOut'].bind('<ButtonRelease-1>', lambda event, action=None: self.choose(action))

        # self.output = tk.Label(self, text="")

        # lay the widgets out on the screen. 
        # self.prompt.pack(side="top", fill="x", pady=(5,global_pady), padx=global_padx)
        # self.output.pack(side="top", fill="x", expand=True)
        self.parent.protocol("WM_DELETE_WINDOW",self.on_exit)
    
    # updates the override variable when user clicks the check box
    def click_check(self):
        self.manual_override['override'] = ( self.var.get() == 1 )

    def choose(self, action):
        self.manual_override['p'] = 0
        self.manual_override['t'] = 0
        self.manual_override['z'] = 0
        self.manual_override['override'] = True
        if action == 'left':
            self.manual_override['p'] = self.amplitude
        elif action == 'right':
            self.manual_override['p'] = -self.amplitude
        elif action == 'up':
            self.manual_override['t'] = self.amplitude
        elif action == 'down':
            self.manual_override['t'] = -self.amplitude
        elif action == 'zoomIn':
            self.manual_override['z'] = self.amplitude
        elif action == 'zoomOut':
            self.manual_override['z'] = -self.amplitude
        elif self.var.get() == 0: 
            self.manual_override['override'] = False

        # print('Chosen action:{}'.format(action))

    def on_exit(self):
        self.chosen_name = None
        self.show_frame = None
        print('Quiting')
        self.parent.destroy()


# if this is run as a program (versus being imported),
# create a root window and an instance of our example,
# then start the event loop

def ui_controller(manual_override, screen_loc=[0,0],  screen_size=None):
    root = tk.Tk()
    root.configure(bg='#81ecec')
    ws = root.winfo_screenwidth()  # width of screen
    hs = root.winfo_screenheight() # height of screen
    est_width = 400
    # print(ws, hs)
    x = screen_loc[0]
    y = screen_loc[1]
    root.geometry('+%d+%d'%(int(x),int(y)))
    ui_controller = Controller(root, manual_override)
    ui_controller.pack(fill="both", expand=True)
    ui_controller.focus_set()
    # ui_thread = Thread(target = root.mainloop, args=())
    # ui_thread.start()
    root.mainloop()
    # print('out of loop Chosen:{}'.format(choser.names[choser.chosen]))
    # return ui_controller

if __name__ == '__main__':
    manual_override = {'p':0, 't':0, 'z':0, 'override':False}
    ui_controller(manual_override)