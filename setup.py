from setuptools import setup

setup(name='youtube_cue',
      version='0.1',
      packages=['youtube_cue'],
      scripts=['youtube-cue'],

      install_requires=['musicbrainzngs', 'lxml', 'requests', 'youtube-dl', 'cssselect'],

      description='youtube-cue',
      url='http://github.com/bugdone/youtube-cue',
      author='bugdone',
      author_email='bugdone@gmail.com',
      license='MIT')
