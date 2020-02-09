class Iterator:
  def __init__(self, iterable):
    self.iterable = iterable
    self.cursor = -1

  def __len__(self):
    return len(self.iterable)

  @property
  def done(self):
    return self.cursor == len(self.iterable) - 1

  @property
  def current(self):
    return self.iterable[self.cursor]

  @property
  def progress(self):
    return (self.cursor + 1) / len(self.iterable)

  def next(self):
    self.cursor += 1

    if (self.cursor < len(self.iterable)):
      return self.iterable[self.cursor]

    return None

  def reset(self):
    self.cursor = -1


class IteratorsDict:
  def __init__(self):
    self.iterators = dict()

  def __setitem__(self, key, value):
    self.iterators[key] = value

  def __getitem__(self, key):
    return self.iterators[key]

  def items(self):
    return self.iterators.items()

  def keys(self):
    return self.iterators.keys()

  def values(self):
    return self.iterators.values()

  @property
  def all_done(self):
    for iterator in self.iterators.values():
      if (not iterator.done):
        return False

    return True