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