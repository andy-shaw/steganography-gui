import tkinter as tk
import SignalBus

class Menubar(tk.Menu):
  def __init__(self, parent, *args, **kwargs):
    tk.Menu.__init__(self, parent, *args, **kwargs)
    self.parent = parent
    self.create_widgets()

    self.bind_signals()

  def create_widgets(self):
    self.file_menu = tk.Menu(self, tearoff=0)
    self.file_menu.add_command(label="Open...", command=lambda: SignalBus.SIG_OPEN.emit())
    self.file_menu.add_command(label="Save...", command=lambda: SignalBus.SIG_SAVE.emit(), state="disabled")
    self.file_menu.add_separator()
    self.file_menu.add_command(label="Exit", command=lambda: SignalBus.SIG_QUIT.emit())

    self.help_menu = tk.Menu(self, tearoff=0)
    self.help_menu.add_command(label="About...", )

    self.add_cascade(label="File", menu=self.file_menu)
    self.add_cascade(label="Help", menu=self.help_menu)

  def bind_signals(self):
    SignalBus.SIG_IMAGE_LOADED.bind(self.handle_open_image)
    SignalBus.SIG_IMAGE_UNLOADED.bind(self.handle_close_image)

  def handle_open_image(self):
    self.file_menu.entryconfigure(1, state="normal")
  def handle_close_image(self):
    self.file_menu.entryconfigure(1, state="disabled")

if __name__ == '__main__':

  # test menubar
  print("test")