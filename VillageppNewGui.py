import tkinter as tk
import PIL

lang = "en"

# TODO: settings.json

lang_data = {
    "File": {
        "en": "File",
        "de": "Datei"},

    "New": {
        "en": "New",
        "de": "Neu"
    }
}

class Villagepp(tk.Tk):
    def __init__(self, master = None):
        tk.Tk.__init__(self)

        self.geometry("640x480")
        self.wm_title("Village++")
        self.iconphoto(False, tk.PhotoImage(file="res/logo_supreme.png"))
        
        
        # menu
        menubar = tk.Menu(self)
        self.config(menu = menubar)

        # file menu
        file_menu = tk.Menu(menubar, tearoff = 0)
        menubar.add_cascade(label=lang_data["File"][lang], menu = file_menu)

        file_menu.add_command(label=lang_data["New"][lang], command = self.test, accelerator = "Ctrl+A")
        self.bind_all("<Control-a>", self.test)
        file_menu.add_command(label = "Open")
        file_menu.add_command(label = "Save")
        file_menu.add_command(label = "Save as...")
        file_menu.add_separator()
        file_menu.add_command(label = "Export...")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command = self.quit)
        
        # view menu
        view_menu = tk.Menu(menubar, tearoff = 0)
        menubar.add_cascade(label= "View", menu = view_menu)

        # help menu
        help_menu = tk.Menu(menubar, tearoff = 0)   
        menubar.add_cascade(label= "Help", menu = help_menu)
        

        # canvas
        # frame_canvas = tk.Frame(self)
        # vpp = tk.PhotoImage(file="res/dickbutt.png")
        # imgLabel = tk.Label(frame_canvas, image=vpp)
        # imgLabel.pack()

        # buttons n stuff

        frame_build = tk.Frame(self)

        # navigation bar
        frame_navbar = tk.Frame(frame_build)
        button_first = tk.Button(frame_navbar, text = "|<")
        button_prev = tk.Button(frame_navbar, text = "<")
        slider_step = tk.Scale(frame_navbar, from_=0, to = 42, orient = tk.HORIZONTAL)

        button_next = tk.Button(frame_navbar, text = ">")
        button_last = tk.Button(frame_navbar, text = ">|")

        button_first.pack(side = tk.LEFT)
        button_prev.pack(side = tk.LEFT)
        slider_step.pack(side = tk.LEFT)
        button_next.pack(side = tk.LEFT)
        button_last.pack(side = tk.LEFT)
        frame_navbar.pack(side = tk.LEFT)



        # pack stuff...
        # frame_canvas.pack(padx=10, pady=10, side=tk.LEFT)
        frame_build.pack(padx=10, pady=10, side=tk.RIGHT)

    def quit(self):
        quit

    def test(self):
        print("Test")

if __name__ == "__main__":
    vpp = Villagepp()
    vpp.mainloop()

# ultra standard size:
# 640x480
# AIV resolution: 1024x768
# AIV resolution only map: 768x768