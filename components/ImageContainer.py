import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import ImageTk, Image
import steganography
import SignalBus
import AppConfig
import Globals
import utils

logger = utils.generate_logger()

class ImageContainer(tk.Frame):
  def __init__(self, parent, *args, **kwargs):
    tk.Frame.__init__(self, parent, *args, **kwargs,  height=f"{AppConfig.MAX_SIZE}", width=f"{AppConfig.MAX_SIZE}")

    self.stegoimage = None
    self.image_container = None
    self.label = None

    self.bind_signals()
    self.create_widgets()


  def create_widgets(self):
    self.stegoimage = steganography.StegoImage()
    if self.stegoimage.image != None:
      self.render_image()

  def render_image(self, use_preview=False):
    if self.stegoimage.image != None:

      # clean if component already exists
      if self.label != None:
        self.label.destroy()
        self.label = None


      widget_image = self.stegoimage.image
      if use_preview:
        widget_image = self.stegoimage.preview

      # calculate dimensions for resize
      l,w = self.stegoimage.image.size
      # print('l,w:', l, ' ', w, ', max size:', AppConfig.MAX_SIZE)
      new_l = l
      new_w = w
      if l > w:
        aspect_ratio = l / w
        new_l = int(AppConfig.MAX_SIZE)
        new_w = int(AppConfig.MAX_SIZE / aspect_ratio)
      else:
        aspect_ratio = w / l
        new_l = int(AppConfig.MAX_SIZE / aspect_ratio)
        new_w = int(AppConfig.MAX_SIZE)

      # perform resize
      if new_w != w or new_l != l:
        # logger.debug(f'resize: {l}x{w} -> {new_l}x{new_w}')
        pass
      widget_image = widget_image.resize((new_l, new_w), Image.Resampling.LANCZOS)

      # build tk components
      self.image_container = ImageTk.PhotoImage(widget_image,  height=f"{AppConfig.MAX_SIZE}", width=f"{AppConfig.MAX_SIZE}")
      self.label = tk.Label(self, image=self.image_container,  height=f"{AppConfig.MAX_SIZE}", width=f"{AppConfig.MAX_SIZE}")
      self.label.pack(side="left", padx=2, pady=2)
      self.label.config(highlightbackground="black", highlightthickness=1)

      # calculate number of bits for global
      Globals.NUM_BITS = int((l * w * 3))

  def write_to_image(self, text):
    self.stegoimage.write_text(text)
    SignalBus.SIG_EDIT.emit()

  def handle_scrub_image(self):
    self.stegoimage.clean_image()
    self.render_image()

  def bind_signals(self):
    SignalBus.SIG_SAVE.bind(self.save_image)
    SignalBus.SIG_OPEN.bind(self.open_image)
    SignalBus.SIG_EMBED.bind(self.write_to_image)
    SignalBus.SIG_EDIT.bind(lambda: self.render_image(True))
    SignalBus.SIG_SCRUB.bind(self.handle_scrub_image)

  # image controls
  def save_image(self):
    if self.stegoimage.image != None:
      self.stegoimage.save_image()
    else:
      # logger.debug("ImageContainer.save_image, no image present")
      pass
  def open_image(self):
    path = filedialog.askopenfilename()
    if path == "":
      return
    self.stegoimage.path = path
    self.stegoimage.open_image()
    if self.stegoimage.image == None:
      messagebox.showerror(title=f"{AppConfig.APPLICATION_NAME}: Error", message="Unable to open image")
    else:
      SignalBus.SIG_IMAGE_LOADED.emit()
      self.render_image()