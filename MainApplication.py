import steganography
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import SignalBus
import Globals
from components import Menubar, ImageContainer, TextInput
import AppConfig

import logging
import logging.config
logging.config.fileConfig('loggers.conf')
logger = logging.getLogger('basicLogger')

class MainApplication(tk.Frame):
  def __init__(self, parent, *args, **kwargs):
    tk.Frame.__init__(self, parent, *args, **kwargs)
    self.parent: tk.Tk = parent

    self.parent.title(AppConfig.APPLICATION_NAME)

    self.bind_signals()
    self.create_widgets()
    self.bind_keybindings()

  def on_quit(self):
    if Globals.UNSAVED:
      confirm_save = messagebox.askyesnocancel(title=f"{AppConfig.APPLICATION_NAME}", message="Do you want to save before closing?")
      if confirm_save == True:
        SignalBus.SIG_SAVE.emit()
        logger.debug("saving complete, continuing with closing of application")
      elif confirm_save == False:
        logger.debug("user opted out of saving before closing")
      elif confirm_save == None:
        logger.debug("save on quit, cancel selected, aborting closing of application")
        return # cancel application quit

    self.parent.quit()

  def create_widgets(self):
    self.menubar = Menubar.Menubar(self.parent)
    self.parent.config(menu=self.menubar)

    self.image_container = ImageContainer.ImageContainer(self.parent)
    self.image_container.pack(side="left")

    self.separator = ttk.Separator(self.parent, orient="vertical")
    self.separator.pack(side='top', fill="y")

    self.text_input = TextInput.TextInput(self.parent)
    self.text_input.pack(side="right", anchor="e")


  def bind_signals(self):
    SignalBus.SIG_QUIT.bind(self.on_quit)

  def bind_keybindings(self):
    logger.debug("Application Keyboard Binding: Escape -> quit")
    self.parent.bind("<Escape>", lambda x: main.on_quit())


if __name__ == '__main__':

  root = tk.Tk()
  main = MainApplication(root)
  main.pack(side="top", fill="both", expand=True)
  root.protocol("WM_DELETE_WINDOW", main.on_quit)
  root.bind("<Escape>", lambda x: main.on_quit())
  root.mainloop()