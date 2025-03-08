import tkinter as tk
import tkinter.scrolledtext as scrolledtext
import SignalBus
import Globals
import steganography
import string

class TextInput(tk.Frame):
  def __init__(self, parent, text="", *args, **kwargs):
    tk.Frame.__init__(self, parent, *args, **kwargs, padx=8, )
    self.parent = parent
    self.text = text

    self.bind_signals()
    self.create_widgets()

  def _update_space_remaining_label(self):
    self.space_remaining_label.config(text=f"({steganography.META_OFFSET + len(self.text)}/{Globals.NUM_BITS // 8})")

  def handle_keystroke(self, event):
    # print('event:', event)
    new_char = event.char
    if event.char not in string.printable:
      new_char =''
    self.text = self.text_area.get("1.0", tk.END)[:-1] + new_char # tk puts a newline at the end of the text_area
    self._update_space_remaining_label()

  def handle_scrub_button_press(self):
    self.text_area.delete('1.0', tk.END)
    self.text = ""
    self._update_space_remaining_label()
    SignalBus.SIG_SCRUB.emit()

  def handle_embed_button_press(self):
    SignalBus.SIG_EMBED.emit(self.text_area.get("1.0", tk.END)[:-1])

  def handle_save_button_press(self):
    SignalBus.SIG_SAVE.emit()

  def bind_signals(self):
    SignalBus.SIG_SAVE.bind(lambda: self.save_button.config(state="disabled"))
    SignalBus.SIG_EMBED.bind(lambda x: self.save_button.config(state="normal"))
    SignalBus.SIG_SCRUB.bind(lambda: self.save_button.config(state="normal"))

  def create_widgets(self):
    self.space_remaining_label = tk.Label(text="(0/0)")
    self.space_remaining_label.pack(side="top")

    self.text_area = scrolledtext.ScrolledText(self, background="white", wrap="word")
    self.text_area.pack(side="top")
    self.text_area.insert(tk.END, self.text)
    self._update_space_remaining_label()

    self.text_area.bind("<Key>", self.handle_keystroke)

    # controls
    self.controls_container = tk.Frame(self)
    self.controls_container.pack(side="right", pady=4, padx=1)

    self.save_button = tk.Button(self.controls_container, text="Save", width=12, command=self.handle_save_button_press, state="disabled")
    self.save_button.pack(side="right")

    self.embed_button = tk.Button(self.controls_container, text="Embed", width=12, command=self.handle_embed_button_press)
    self.embed_button.pack(side="right")

    self.clear_button = tk.Button(self.controls_container, text="Scrub", command=self.handle_scrub_button_press, width=12)
    self.clear_button.pack(side="right")
