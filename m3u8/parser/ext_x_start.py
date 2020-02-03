from m3u8.parser.attribute_list import M3U8_AttributeListFactory


class M3U8_Ext_X_Start:
  def __init__(self, attr_list):
    self.time_offset = None
    self.precise = 'NO'

    if ('TIME-OFFSET' in attr_list.parsed):
      attr = attr_list['TIME-OFFSET']
      if (attr.type != M3U8_AttributeListFactory.ATTR_TYPE_DECIMAL_FLOATING_POINT and attr.type != M3U8_AttributeListFactory.ATTR_TYPE_SIGNED_DECIMAL_FLOATING_POINT):
        raise Exception('TIME-OFFSET must be of type decimal-floating-point or signed-decimal-floating-point')
      self.time_offset = float(attr.value)

    if ('PRECISE' in attr_list.parsed):
      attr = attr_list['PRECISE']
      if (attr.type != M3U8_AttributeListFactory.ATTR_TYPE_ENUMERATED_STRING):
        raise Exception('PRECISE must be of type enumerated-string')
      if (attr.value != 'YES' and attr.value != 'NO'):
        raise Exception(f'{attr.value} is not valid value for PRECISE attr')
      self.precise = attr.value

    if (self.time_offset is None):
      raise Exception('Missing required attr TIME-OFFSET')