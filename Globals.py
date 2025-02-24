import SignalBus

UNSAVED = False
IMAGE_LOADED = False
NUM_BITS = 0

def set_unsaved(val):
  global UNSAVED
  UNSAVED = val
def set_image_loaded(val):
  global IMAGE_LOADED
  IMAGE_LOADED = val



SignalBus.SIG_SAVE.bind(lambda: set_unsaved(False), caller="Globals.py")
SignalBus.SIG_IMAGE_LOADED.bind(lambda: set_unsaved(False), caller="Globals.py")
SignalBus.SIG_IMAGE_LOADED.bind(lambda: set_image_loaded(True), caller="Globals.py")
SignalBus.SIG_IMAGE_LOADED.bind(lambda: set_image_loaded(True), caller="Globals.py")
