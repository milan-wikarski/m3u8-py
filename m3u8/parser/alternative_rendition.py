from m3u8.parser.attribute_list import M3U8_AttributeListFactory as ALF


class M3U8_AlternativeRendition:
  def __init__(self, attr_list):
    self.type = None
    self.url = None
    self.group_id = None
    self.language = None
    self.assoc_language = None
    self.name = None
    self.default = 'NO'
    self.autoselect = 'NO'
    self.forced = 'NO'
    self.instream_id = None
    self.characteristics = []
    self.channels = []

    if ('TYPE' in attr_list.parsed):
      attr = attr_list['TYPE']
      if (attr.type != ALF.ATTR_TYPE_ENUMERATED_STRING):
        raise Exception('TYPE must be of type enumerated-string')
      if (not attr.value in ['AUDIO', 'VIDEO', 'SUBTITLES', 'CLOSED-CAPTIONS']):
        raise Exception(f'{attr.value} is not valid value of TYPE')
      self.type = attr.value

    if ('URI' in attr_list.parsed):
      attr = attr_list['URI']
      if (attr.type != ALF.ATTR_TYPE_QUOTED_STRING):
        raise Exception('URI must be of type quoted-string')
      self.url = attr.value

    if ('GROUP-ID' in attr_list.parsed):
      attr = attr_list['GROUP-ID']
      if (attr.type != ALF.ATTR_TYPE_QUOTED_STRING):
        raise Exception('GROUP-ID must be of type quoted-string')
      self.group_id = attr.value

    if ('LANGUAGE' in attr_list.parsed):
      attr = attr_list['LANGUAGE']
      if (attr.type != ALF.ATTR_TYPE_QUOTED_STRING):
        raise Exception('LANGUAGE must be of type quoted-string')
      self.language = attr.value

    if ('ASSOC-LANGUAGE' in attr_list.parsed):
      attr = attr_list['ASSOC-LANGUAGE']
      if (attr.type != ALF.ATTR_TYPE_QUOTED_STRING):
        raise Exception('ASSOC-LANGUAGE must be of type quoted-string')
      self.assoc_language = attr.value

    if ('NAME' in attr_list.parsed):
      attr = attr_list['NAME']
      if (attr.type != ALF.ATTR_TYPE_QUOTED_STRING):
        raise Exception('NAME must be of type quoted-string')
      self.name = attr.value

    if ('DEFAULT' in attr_list.parsed):
      attr = attr_list['DEFAULT']
      if (attr.type != ALF.ATTR_TYPE_ENUMERATED_STRING):
        raise Exception('DEFAULT must be of type enumerated-string')
      if (attr.value != 'YES' and attr.value != 'NO'):
        raise Exception(f'{attr.value} is not valid value of DEFAULT')
      self.default = attr.value

    if ('AUTOSELECT' in attr_list.parsed):
      attr = attr_list['AUTOSELECT']
      if (attr.type != ALF.ATTR_TYPE_ENUMERATED_STRING):
        raise Exception('AUTOSELECT must be of type enumerated-string')
      if (attr.value != 'YES' and attr.value != 'NO'):
        raise Exception(f'{attr.value} is not valid value of AUTOSELECT')
      self.autoselect = attr.value

    if ('FORCED' in attr_list.parsed):
      attr = attr_list['FORCED']
      if (attr.type != ALF.ATTR_TYPE_ENUMERATED_STRING):
        raise Exception('FORCED must be of type enumerated-string')
      if (attr.value != 'YES' and attr.value != 'NO'):
        raise Exception(f'{attr.value} is not valid value of FORCED')
      self.forced = attr.value

    if ('INSTREAM-ID' in attr_list.parsed):
      attr = attr_list['INSTREAM-ID']
      if (attr.type != ALF.ATTR_TYPE_QUOTED_STRING):
        raise Exception('INSTREAM-ID must be of type quoted-string')
      self.instream_id = attr.value

    if ('CHARACTERISTICS' in attr_list.parsed):
      attr = attr_list['CHARACTERISTICS']
      if (attr.type != ALF.ATTR_TYPE_QUOTED_STRING):
        raise Exception('CHARACTERISTICS must be of type quoted-string')
      self.characteristics = attr.value.split(',')

    if ('CHANNELS' in attr_list.parsed):
      attr = attr_list['CHANNELS']
      if (attr.type != ALF.ATTR_TYPE_QUOTED_STRING):
        raise Exception('CHANNELS must be of type quoted-string')
      self.channels = attr.value.split('/')

    if (self.type is None):
      raise Exception('Missing required attr TYPE')

    if (self.group_id is None):
      raise Exception('Missing required attr GROUP-ID')

    if (self.name is None):
      raise Exception('Missing required attr NAME')

  def __str__(self):
    return '\n'.join([
      f'           type --> {self.type}',
      f'            url --> {self.url}',
      f'       group_id --> {self.group_id}',
      f'       language --> {self.language}',
      f' assoc_language --> {self.assoc_language}',
      f'           name --> {self.name}',
      f'        default --> {self.default}',
      f'     autoselect --> {self.autoselect}',
      f'         forced --> {self.forced}',
      f'    instream_id --> {self.instream_id}',
      f'characteristics --> {self.characteristics}',
      f'       channels --> {self.channels}'
    ])