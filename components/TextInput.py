import tkinter as tk
import SignalBus
import Globals
import re
import steganography

class TextInput(tk.Frame):
  def __init__(self, parent, *args, **kwargs):
    tk.Frame.__init__(self, parent, *args, **kwargs, padx=8)
    self.parent = parent
    self.text = ""

    self.create_widgets()

  def _update_space_remaining_label(self):
    self.space_remaining_label.config(text=f"({steganography.META_OFFSET + len(self.text)}/{Globals.NUM_BITS // 8})")

  def handle_keystroke(self, event):
    self.text = self.text_area.get("1.0", tk.END)[:-1] + event.char # tk puts a newline at the end of the text_area
    self._update_space_remaining_label()

  def handle_clear_button_press(self):
    self.text_area.delete('1.0', tk.END)
    self.text = ""

  def handle_embed_button_press(self):
    SignalBus.SIG_EMBED.emit(self.text_area.get("1.0", tk.END)[:-1])

  def handle_save_button_press(self):
    SignalBus.SIG_SAVE.emit()

  def create_widgets(self):
    self.space_remaining_label = tk.Label(text="(0/0)")
    self.space_remaining_label.pack(side="top")

    self.text_area = tk.Text(self, height=5, background="white")
    self.text_area.pack(side="top")
    self.text_area.insert(tk.END, steganography.DEBUG_TEXT)
    self.text = steganography.DEBUG_TEXT
    self._update_space_remaining_label()

    self.text_area.bind("<Key>", self.handle_keystroke)

    # controls
    self.controls_container = tk.Frame(self)
    self.controls_container.pack(side="right", pady=4, padx=1)

    self.save_button = tk.Button(self.controls_container, text="Save", width=12, command=self.handle_save_button_press)
    self.save_button.pack(side="right")

    self.embed_button = tk.Button(self.controls_container, text="Embed", width=12, command=self.handle_embed_button_press)
    self.embed_button.pack(side="right")

    self.revert_button = tk.Button(self.controls_container, text="Revert", width=12)
    self.revert_button.pack(side="right")

    self.clear_button = tk.Button(self.controls_container, text="Clear", command=self.handle_clear_button_press, width=12)
    self.clear_button.pack(side="right")
