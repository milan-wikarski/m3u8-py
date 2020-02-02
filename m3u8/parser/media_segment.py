class M3U8_MediaSegment:
  def __init__(self):
    self.url = None
    self.duration = None
    self.title = None
    self.byterange = None
    self.byterange_offset = None
    self.discontinuity = False
    self.program_datetime = None

  def __str__(self):
    return '\n'.join([
      f'             URL --> {self.url}',
      f'        duration --> {self.duration}',
      f'           title --> {self.title}',
      f'       byterange --> {self.byterange}',
      f'byterange_offset --> {self.byterange_offset}'
    ])

  @property
  def is_valid(self):
    return self.url is not None and self.duration is not None