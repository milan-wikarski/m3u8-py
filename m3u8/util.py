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


class URIValidator:
  regex = regex = re.compile(
    r'^(?:http|ftp)s?://' # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
    r'localhost|' #localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
    r'(?::\d+)?' # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE
  )

  @staticmethod
  def is_valid(uri):
    return re.match(URIValidator.regex, uri) is not None