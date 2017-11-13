from setuptools import setup

setup(name='youtube_cue',
      version='0.1',
      packages=['youtube_cue'],
      scripts=['youtube-cue'],

      install_requires=['musicbrainzngs', 'lxml', 'requests', 'youtube-dl', 'cssselect'],

      description='youtube-cue',
      url='https://github.com/bugdone/youtube-cue',
      download_url='https://github.com/bugdone/youtube-cue/archive/0.1.tar.gz',
      keywords=['youtube', 'cue'],
      author='bugdone',
      author_email='bugdone@gmail.com',
      license='MIT')
