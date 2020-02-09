import os


class PathFile:
  def __init__(self, path, mode):
    self.path = path
    self.file = open(path, mode)

  def close(self):
    self.file.close()

  def remove(self):
    os.remove(self.path)

  @property
  def abspath(self):
    return str(self.path.absolute())