from m3u8.attribute_list import M3U8_AttributeListFactory


class M3U8_VariantStream:
  def __init__(self, attr_list, uri):
    self.uri = uri
    self.bandwidth = None
    self.average_bandwidth = None
    self.codecs = None
    self.resolution = None
    self.frame_rate = None
    self.hdcp_level = None
    self.audio = None
    self.video = None
    self.subtitles = None
    self.closed_captions = None
    
    for key in attr_list.parsed:
      attr = attr_list[key]

      # BANDWIDTH
      if (key == 'BANDWIDTH'):
        if (attr.type != M3U8_AttributeListFactory.ATTR_TYPE_DECIMAL_INTEGER):
          raise Exception('BANDWIDTH must be of type decimal-integer')
        self.bandwidth = attr.value

      # AVERAGE-BANDWIDTH
      elif (key == 'AVERAGE-BANDWIDTH'):
        if (attr.type != M3U8_AttributeListFactory.ATTR_TYPE_DECIMAL_INTEGER):
          raise Exception('AVERAGE-BANDWIDTH must be of type decimal-integer')
        self.average_bandwidth = attr.value
          
      # CODECS
      elif (key == 'CODECS'):
        if (attr.type != M3U8_AttributeListFactory.ATTR_TYPE_QUOTED_STRING):
          raise Exception('CODECS must be of type quoted-string')
        self.codecs = attr.value.split(',')

      # RESOLUTION
      elif (key == 'RESOLUTION'):
        if (attr.type != M3U8_AttributeListFactory.ATTR_TYPE_DECIMAL_RESOLUTION):
          raise Exception('RESOLUTION must be of type decimal-resolution')
        self.resolution = attr.value

      # FRAME-RATE
      elif (key == 'FRAME-RATE'):
        if (attr.type != M3U8_AttributeListFactory.ATTR_TYPE_DECIMAL_FLOATING_POINT):
          raise Exception('FRAME-RATE must be of type decimal-floating-point')
        self.frame_rate = attr.value

      # HDCP-LEVEL
      elif (key == 'HDCP-LEVEL'):
        if (attr.type != M3U8_AttributeListFactory.ATTR_TYPE_ENUMERATED_STRING):
          raise Exception('HDCP-LEVEL must be of type enumerated-string')
        self.hdcp_level = attr.value

      # AUDIO
      elif (key == 'AUDIO'):
        if (attr.type != M3U8_AttributeListFactory.ATTR_TYPE_QUOTED_STRING):
          raise Exception('AUDIO must be of type quoted-string')
        self.audio = attr.value

      # VIDEO
      elif (key == 'VIDEO'):
        if (attr.type != M3U8_AttributeListFactory.ATTR_TYPE_QUOTED_STRING):
          raise Exception('VIDEO must be of type quoted-string')
        self.video = attr.value

      # SUBTITLES
      elif (key == 'SUBTITLES'):
        if (attr.type != M3U8_AttributeListFactory.ATTR_TYPE_QUOTED_STRING):
          raise Exception('SUBTITLES must be of type quoted-string')
        self.subtitles = attr.value

      # CLOSED-CAPTIONS
      elif (key == 'CLOSED-CAPTIONS'):
        if (attr.type != M3U8_AttributeListFactory.ATTR_TYPE_QUOTED_STRING and attr.type != M3U8_AttributeListFactory.ATTR_TYPE_ENUMERATED_STRING):
          raise Exception('CLOSED-CAPTIONS must be of type quoted-string or enumerated-string')
        self.closed_captions = attr.value

    if (self.bandwidth is None):
      raise Exception('Missing required attr BANDWIDTH')

  def __str__(self):
    return '\n'.join([
      f'              URI --> {self.uri}',
      f'        bandwidth --> {self.bandwidth}',
      f'average_bandwidth --> {self.average_bandwidth}',
      f'           codecs --> {self.codecs}',
      f'       resolution --> {self.resolution}',
      f'       frame_rate --> {self.frame_rate}',
      f'       hdcp_level --> {self.hdcp_level}',
      f'            audio --> {self.audio}',
      f'            video --> {self.video}',
      f'        subtitles --> {self.subtitles}',
      f'  closed_captions --> {self.closed_captions}'
    ])
