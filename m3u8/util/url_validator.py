import re


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

