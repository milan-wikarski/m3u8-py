import re
from m3u8.util import Iterator

class M3U8_AttributeList:
  def __init__(self, parsed):
    self.parsed = parsed

  def __str__(self):
    res = []
    
    for key in self.parsed:
      res.append(f'{key} --> {self.parsed[key].__str__()}')

    return '\n'.join(res)

  def __getitem__(self, attr):
    return self.parsed[attr]


class M3U8_Attribute:
  def __init__(self, value, type):
    self.value = value
    self.type = type

  def __str__(self):
    return f'<{M3U8_AttributeListFactory.ATTR_TYPES[self.type]}>: {self.value}'


class M3U8_AttributeListFactory:
  ATTR_TYPE_DECIMAL_INTEGER = 0
  ATTR_TYPE_HEXADECIMAL_SEQUENCE = 1
  ATTR_TYPE_DECIMAL_FLOATING_POINT = 2
  ATTR_TYPE_SIGNED_DECIMAL_FLOATING_POINT = 3
  ATTR_TYPE_DECIMAL_RESOLUTION = 4
  ATTR_TYPE_QUOTED_STRING = 5
  ATTR_TYPE_ENUMERATED_STRING = 6

  ATTR_TYPES = [
    'decimal-integer',
    'hexadecimal-sequence',
    'decimal-floating-point',
    'signed-decimal-floating-point',
    'decimal-resolution',
    'quoted-string',
    'enumerated-string'
  ]    

  @staticmethod
  def create(raw):
    parsed = dict()

    # Parse comma separated values to get pairs
    pairs = []
    iterator = Iterator(raw)
    start = 0
    inside_quote = False
    while (True):
      if (iterator.done):
        pairs.append(raw[start:])
        break

      char = iterator.next()
      
      if (char == '"'):
        inside_quote = not inside_quote
      
      if (not inside_quote and char == ','):
        pairs.append(raw[start:(iterator.cursor)])
        start = iterator.cursor + 1

    # Parse each pair
    for pair in pairs:
      key, value = pair.split("=")

      # Check the validity of characters
      match = re.match('[A-Z0-9\-]+', key)
      if (match is None):
        raise Exception('Invalid symbols in attribute name')

      start, end = match.span()
      if ((end - start) != len(key)):
        raise Exception('Invalid symbols in attribute name')
      
      # Check the uniqueness of key
      if (key in parsed):
        raise Exception(f'Attribute {key} appeared multiple times in attribute list')

      # 0: decimal-integer
      if (re.match('^\d{1,20}$', value)):
        parsed[key] = M3U8_Attribute(int(value), M3U8_AttributeListFactory.ATTR_TYPE_DECIMAL_INTEGER)

      # 1: hexadecimal-sequence
      elif (re.match('^0(x|X)[0-9A-F]+$', value)):
        parsed[key] = M3U8_Attribute(value[2:], M3U8_AttributeListFactory.ATTR_TYPE_HEXADECIMAL_SEQUENCE)

      # 2: decimal-floating-point
      elif (re.match('^\d+\.\d+$', value)):
        parsed[key] = M3U8_Attribute(float(value), M3U8_AttributeListFactory.ATTR_TYPE_DECIMAL_FLOATING_POINT)

      # 3: signed-decimal-floating-point
      elif (re.match('^\-\d+\.\d+$', value)):
        parsed[key] = M3U8_Attribute(float(value), M3U8_AttributeListFactory.ATTR_TYPE_DECIMAL_FLOATING_POINT)

      #4: decimal-resolution
      elif (re.match('^(\d)+x(\d)+', value)):
        parsed[key] = M3U8_Attribute(tuple(map(int, value.split('x'))), M3U8_AttributeListFactory.ATTR_TYPE_DECIMAL_RESOLUTION)

      # 5: quoted-string
      elif (re.match('^"[^\n\r"]+"$', value)):
        parsed[key] = M3U8_Attribute(value[1:(len(value) - 1)], M3U8_AttributeListFactory.ATTR_TYPE_QUOTED_STRING)

      # 6: enumerated-string
      elif (re.match('^[^ \n\r",]+$', value)):
        parsed[key] = M3U8_Attribute(value, M3U8_AttributeListFactory.ATTR_TYPE_ENUMERATED_STRING)

      else:
        raise Exception(f'Invalid attribute type: {key}={value}')

    return M3U8_AttributeList(parsed)