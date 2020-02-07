import re


class Iterator:
  def __init__(self, iterable):
    self.iterable = iterable
    self.cursor = -1

  @property
  def done(self):
    return self.cursor == len(self.iterable) - 1

  @property
  def current(self):
    return self.iterable[self.cursor]

  def next(self):
    self.cursor += 1

    if (self.cursor < len(self.iterable)):
      return self.iterable[self.cursor]

    return None

  def reset(self):
    self.cursor = -1


class URLValidator:
  regex = regex = re.compile(
    r'^(?:http|ftp)s?://' # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
    r'localhost|' #localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
    r'(?::\d+)?' # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE
  )

  @staticmethod
  def is_valid(url):
    return re.match(URLValidator.regex, url) is not None

  @staticmethod
  def locate_resource(base, path, resource):
    # Full path
    if (URLValidator.is_valid(resource)):
      return resource
    # Absolute path
    elif (resource[0] == '/'):
      return base + resource
    # Relative path
    else:
      return base + path + resource

def int_input(low=None, high=None):
  """
  Reads int form console.
  Low and High limit can be specified.
  Low is inclusive (>=)
  High is exclusive (<)
  """
  res = None
  while (True):
    print(' > ', end='')
    try:
      res = int(input())
      if ((low is None or res >= low) and (high is None or res < high)):
        break
    except:
      pass
  
  return res