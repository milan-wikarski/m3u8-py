class M3U8_MediaSegment:
  def __init__(self):
    self.uri = None
    self.duration = None
    self.title = None

  def __str__(self):
    return '\n'.join([
      f'uri      --> {self.uri}',
      f'duration --> {self.duration}',
      f'title    --> {self.title}'
    ])

  @property
  def is_valid(self):
    return self.uri is not None and self.duration is not None