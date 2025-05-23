import steganography
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import SignalBus
import Globals
from components import Menubar, ImageContainer, TextInput
import AppConfig
import utils

logger = utils.generate_logger()

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
        # logger.debug("saving complete, continuing with closing of application")
      elif confirm_save == False:
        # logger.debug("user opted out of saving before closing")
        pass
      elif confirm_save == None:
        # logger.debug("save on quit, cancel selected, aborting closing of application")
        return # cancel application quit

    self.parent.quit()

  def handle_image_loaded(self):
    text = ""
    if self.image_container.stegoimage.image != None:
      try:
        text = self.image_container.stegoimage.read_text()
        self.image_container.stegoimage.show_used_space(self.image_container.stegoimage.num_bits)
        self.image_container.render_image(use_preview=True)

        # coupled functions
        self.text_input.text_area.delete("1.0", tk.END)
        self.text_input.text_area.insert(tk.END, text)
        self.text_input.text = text
        self.text_input._update_space_remaining_label()
      except:
        pass


  def create_widgets(self):
    self.menubar = Menubar.Menubar(self.parent)
    self.parent.config(menu=self.menubar)

    self.image_container = ImageContainer.ImageContainer(self.parent)
    self.image_container.pack(side="left")

    self.separator = ttk.Separator(self.parent, orient="vertical")
    self.separator.pack(side='top', fill="y")

    text = ""
    if self.image_container.stegoimage.image != None:
      try:
        text = self.image_container.stegoimage.read_text()
        self.image_container.stegoimage.show_used_space(self.image_container.stegoimage.num_bits)
        self.image_container.render_image(use_preview=True)
      except:
        pass

    self.text_input = TextInput.TextInput(self.parent, text=text)
    self.text_input.pack(side="right", anchor="e")


  def bind_signals(self):
    SignalBus.SIG_QUIT.bind(self.on_quit)
    SignalBus.SIG_IMAGE_LOADED.bind(self.handle_image_loaded)

  def bind_keybindings(self):
    # logger.debug("Application Keyboard Binding: Escape -> quit")
    self.parent.bind("<Escape>", lambda x: main.on_quit())


if __name__ == '__main__':

  root = tk.Tk()
  main = MainApplication(root)
  main.pack(side="top", fill="both", expand=True)
  root.protocol("WM_DELETE_WINDOW", main.on_quit)
  root.bind("<Escape>", lambda x: main.on_quit())
  root.mainloop()