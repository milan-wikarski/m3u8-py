class M3U8_Playlist:
	def __init__(self):
		self.ext_x_version = None


class M3U8_Playlist_Master(M3U8_Playlist):
	def __init__(self):
		super(M3U8_Playlist_Master, self).__init__()
		self.variant_streams = []

	def __str__(self):
		res = [
			'EXT-X-VERSION',
			f'  {self.ext_x_version}',
			'',
			'VARIANT STREAMS',
		]

		res += [f'{stream.__str__()}\n' for stream in self.variant_streams]

		return '\n'.join(res)

	def add_stream(self, stream):
		self.variant_streams.append(stream)


class M3U8_Playlist_Media(M3U8_Playlist):
	def __init__(self):
		super(M3U8_Playlist_Media, self).__init__()
		self.ext_x_targetduration = None
		self.ext_x_media_sequence = 0
		self.ext_x_media_discontinuity_sequence = 0
		self.ext_x_endlist = False
		self.ext_x_playlist_type = None
		self.ext_x_i_frames_only = False
		self.media_segments = dict()

	def __str__(self):
		res = [
			'EXT-X-VERSION',
			f'  {self.ext_x_version}',
			'',
			'MEDIA SEGMENTS',
		]

		res += [f'{key}\n{self.media_segments[key].__str__()}\n' for key in self.media_segments]

		return '\n'.join(res)

	def add_segment(self, segment):
		sequence = self.ext_x_media_sequence + len(self.media_segments)
		self.media_segments[sequence] = segment

