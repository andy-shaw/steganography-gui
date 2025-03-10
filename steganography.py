from PIL import Image
import os
import sys
import math
import utils

logger = utils.generate_logger()

META_OFFSET = 75 # characters

# META DATA
# encoding (ascii, utf-8, utf-16, utf-32)
# bitlength of data

ENCODINGS_BIT_LENGTH = {
  'ascii': 8,
  'utf-8': 8,
  'utf-16': 16,
  'utf-32': 32,
}

class StegoImage:

  def __init__(self, path: str = "", encoding: str = "ascii"):
    self.path: str = path
    self.image: Image = None
    self.meta = {
      "version": "1.0.0",
    }
    self.encoding: str = encoding
    self.num_bits = -1

    self.preview: Image = None # image with a negative for the pixels that contain bits, rendered on self.write_text

    if os.path.exists(self.path):
      self.open_image()
    else:
      logger.debug(f"image path not found: {self.path}")
      pass

  def open_image(self):
    '''load image into object'''
    logger.info(f"loading path: {self.path}")
    self.image: Image = None
    self.preview: Image = None
    if os.path.exists(self.path):
      try:
        self.image: Image = Image.open(self.path)
        self.preview: Image = self.image.copy()

        l: int = 0
        w: int = 0
        l,w = self.image.size
        logger.info(f"{l}px by {w}px, {l*w} total pixels, {l*w*3} total bits, {int((l*w*3 - META_OFFSET) / 8 )} ascii chars")

      except:
        # logger.error("Error: path is not an image")
        pass
    else:
      logger.error("Error: file not found")
      pass

  def close_image(self):
    self.image.save()
    self.image.close()

  def clean_image(self, num_bits: int = None):
    '''sets the least significant bit to 0 of each RGB value in the image'''
    if self.image == None:
      return

    logger.debug(f"clean_image, num_bits:{num_bits}")

    l, w = self.image.size

    if num_bits == None:
      num_bits = l * w * 3

    b_index: int = 0
    i: int = 0
    while i < l and b_index < num_bits:
      j: int = 0
      while j < w and b_index < num_bits:
        r,g,b,a = self.image.getpixel((i,j))
        b_index += 3

        # set pixels to even numbers
        r = int(r/2) * 2
        g = int(g/2) * 2
        b = int(b/2) * 2

        self.image.putpixel((i,j), (r,g,b,a))
        j += 1
      i += 1

  def _detemine_bit(self, color: int, index: int, binary_string: str):
    '''add to passed in color value'''
    if index >= len(binary_string):
      return color

    if binary_string[index] == '1':
      return color + 1

    # bit value is 0
    return color

  def write_text(self, text: str, encoding: str="ascii"):
    '''calc bit array and write to picture'''

    if self.image == None:
      return

    # logger.debug('writing:"' + text[:55] + ('...' if len(text) > 55 else '') + '" to image')


    #calculate meta
    meta: str = self.meta['version'] + ';'
    meta += f'{META_OFFSET * 8 + len(text) * 8};'
    meta += f'{self.encoding};'
    # logger.debug(f"meta to embed: '{meta}'")

    ascii_bits: str = str(meta.ljust(META_OFFSET) + text).encode('ascii', errors='replace') # uses '?' for non-ascii chars
    bits: int = bin(int.from_bytes(ascii_bits, 'big'))
    self.num_bits = len(bits)

    logger.info(f"{len(bits)} bits to embed in image using {math.ceil(len(bits) / 3)} pixels")
    # print(bits)

    self.clean_image(self.num_bits)

    b_index: int = 0
    l,w = self.image.size

    i: int = 0
    j: int = 0
    while i < l and b_index <= len(bits):
      j = 0
      while j < w and b_index <= len(bits):
        r,g,b,a = self.image.getpixel((i,j))

        r = self._detemine_bit(r, b_index, bits)
        b_index += 1
        g = self._detemine_bit(g, b_index, bits)
        b_index += 1
        b = self._detemine_bit(b, b_index, bits)
        b_index += 1

        self.image.putpixel((i,j), (r,g,b,a))

        j += 1
      i += 1

    self.render_preview(len(bits))

  def render_preview(self, num_bits: int):
    self.preview = self.image.copy()
    b_index: int = 0
    l,w = self.preview.size
    i: int = 0
    j: int = 0
    while i < l and b_index < num_bits:
      j = 0
      while j < w and b_index < num_bits:
        b_index += 3 #increment bits
        r,g,b,a = self.preview.getpixel((i,j))
        r = 255-r
        g = 255-g
        b = 255-b
        self.preview.putpixel((i,j), (r,g,b,int(a/2)))

        j += 1
      i += 1

  def save_image(self):
    logger.info(f"saving image to {self.path}")
    self.image.save(open(self.path, 'wb'))

  def extract_meta(self):
    '''attempt to parse out meta information from header info in image'''
    if self.image == None:
      return

    # read in meta bits
    b_index: int = 0
    meta_bits: int = META_OFFSET * 8
    i: int = 0
    l, w = self.image.size

    bits: str = ''

    while i < l and b_index < meta_bits:
      j: int = 0
      while j < w and b_index < meta_bits:
        r,g,b,a = self.image.getpixel((i,j))

        bits += '0' if r % 2 == 0 else '1'
        b_index += 1
        if b_index > meta_bits: break

        bits += '0' if g % 2 == 0 else '1'
        b_index += 1
        if b_index > meta_bits: break

        bits += '0' if b % 2 == 0 else '1'
        b_index += 1
        if b_index > meta_bits: break

        j += 1
      i += 1

    n: int = int('0b' + bits, 2)
    meta: str = n.to_bytes((n.bit_length() + 7) // 8, 'big').decode('ascii', errors='replace')

    logger.debug("extracted meta: " + meta)
    meta = meta.split(';')

    self.meta['version'] = meta[0]
    self.num_bits = int(meta[1])
    self.encoding = meta[2]


  def read_text(self):
    '''attempt to read text stored in image'''

    if self.image == None:
      return

    self.extract_meta()

    # generate byte array
    bits: str = ''
    l,w = self.image.size
    i: int = 0
    while i < l and len(bits) < self.num_bits:
      j: int = 0
      while j < w and len(bits) < self.num_bits:

        r,g,b,a = self.image.getpixel((i,j))
        # print(f'read:{i},{j}, px: {[r,g,b,a]}')

        bits += '0' if r % 2 == 0 else '1'
        if len(bits) >= self.num_bits: break

        bits += '0' if g % 2 == 0 else '1'
        if len(bits) >= self.num_bits: break

        bits += '0' if b % 2 == 0 else '1'
        if len(bits) >= self.num_bits: break

        j += 1
      i += 1

    self.num_bits = len(bits)
    n = int('0b' + bits, 2)
    text = n.to_bytes((n.bit_length() + 7) // 8, 'big').decode('ascii', errors='replace')

    return text[META_OFFSET:]



DEBUG_TEXT: str = '''Lorem ipsum odor amet, consectetuer adipiscing elit. Nostra eros mi neque hendrerit blandit. Justo odio elit dolor augue maecenas cursus lectus. Montes fusce tempus platea fusce leo. Montes iaculis viverra porttitor hendrerit nisi egestas eleifend lorem. Tellus phasellus parturient dis purus mattis, eleifend mauris rhoncus? Condimentum egestas nibh ligula lorem ultricies phasellus; senectus adipiscing. Nisl ad gravida ad rutrum suspendisse curabitur duis aliquet. Eros feugiat eget euismod interdum congue orci aptent nullam. Nam hac aenean conubia accumsan aliquet turpis vivamus nam.

Suscipit risus dis faucibus pulvinar nostra pharetra finibus volutpat sapien. Aliquam fames leo dolor rhoncus interdum. Montes maximus eget fermentum mi blandit lacus habitasse pretium aenean. Risus dignissim cursus laoreet lacinia; neque hendrerit libero efficitur. Luctus odio scelerisque eros id luctus elementum nec nibh. Maecenas aenean auctor dis per iaculis. Dignissim nibh tincidunt curae aenean velit vel lacus eu.

Euismod taciti non tempor condimentum placerat curabitur primis id. Magnis maecenas mattis viverra laoreet quisque aliquet habitant. Leo auctor convallis metus egestas libero. Congue commodo metus amet massa leo diam. Mauris gravida facilisi primis ullamcorper nullam himenaeos orci gravida cras. Euismod malesuada sagittis enim nulla luctus dui suspendisse tristique. Dapibus ut sem potenti posuere et ligula non et.

Aptent vulputate id egestas rutrum eleifend egestas. Volutpat dictum turpis in donec vitae varius ultricies. Ornare ut ridiculus phasellus integer interdum. Felis facilisis consequat elementum rhoncus ligula. Vestibulum mollis netus tempus id facilisis sit feugiat lacus. Ornare feugiat mattis nisi orci eleifend primis nullam. Non laoreet risus phasellus justo venenatis adipiscing metus.

Lobortis fames convallis gravida risus metus dui nam. Netus accumsan magna cras suspendisse torquent placerat. Velit nec arcu ac neque condimentum pellentesque phasellus parturient. Lorem per curae a velit proin faucibus nisi diam dui. Sem suscipit auctor nec nunc cursus nisl a. Ultricies diam tellus platea quam facilisi praesent iaculis felis. Commodo ad urna ut duis; non porttitor aliquam nostra. Lorem tristique rutrum sollicitudin turpis convallis dictum finibus conubia. Penatibus conubia porta inceptos pulvinar dis tempor habitant ridiculus.

''' * 15

if __name__ == '__main__':

  logger.debug("starting")

  stego = StegoImage('.\\test-data\\image.png')
  stego.clean_image()
  stego.write_text(DEBUG_TEXT)
  stego.preview.show()
  stego.extract_meta()
  # print(stego.read_text())
  assert stego.read_text() == DEBUG_TEXT
  stego.save_image()