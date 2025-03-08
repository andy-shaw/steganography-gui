import inspect
import utils

logger = utils.generate_logger()

class Signal:
  def __init__(self, name):
    self.name = name
    self.bindings = {}

    # logger.debug(f"<Signal: {self.name} created >")

  def bind(self, method, caller=None):
    if caller == None:
      stack = inspect.stack()
      # create an automatic calling footprint
      caller = stack[1][0].f_locals["self"].__class__.__name__ + "." + stack[1][0].f_code.co_name
    if caller not in self.bindings:
      self.bindings[caller] = []
    # logger.debug(f"<Signal: {self.name}, bind: {caller}>")
    self.bindings[caller].append(method)

  def unbind(self, caller):
    if caller in self.bindings.keys():
      del self.bindings[caller]

  def emit(self, *args, **kwargs):
    stack = inspect.stack()
    #  '{stack[1][4][0].strip()}'
    # logger.info(f"<Signal: {self.name}, emit, emitter: '{stack[1][4][0].strip()}' >")
    for handler,methods in self.bindings.items():
      # logger.debug(f"handler:{handler} n:{len(methods)}")
      for binding in methods:
        binding(*args, **kwargs)

# global signals
SIG_IMAGE_LOADED = Signal("SIG_IMAGE_LOADED")
SIG_IMAGE_UNLOADED = Signal("SIG_IMAGE_UNLOADED")
SIG_UPDATE_TEXT = Signal("SIG_UPDATE_TEXT")
SIG_OPEN = Signal("SIG_OPEN")
SIG_SCRUB = Signal("SIG_SCRUB")
SIG_EMBED = Signal("SIG_EMBED")
SIG_EDIT = Signal("SIG_EDIT")
SIG_SAVE = Signal("SIG_SAVE")
SIG_QUIT = Signal("SIG_QUIT")
