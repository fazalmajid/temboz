import setuptools

setuptools.setup(
  name='temboz',
  author='Fazal Majid',
  author_email='python@sentfrom.com',
  version='2.3.1',
  url='http://github.com/fazalmajid/temboz',
  #package_dir={'': 'src'},
  packages=['tembozapp'],
  include_package_data=True,
  scripts=['temboz'],
  install_requires=[
    'flask',
    'requests',
    'html5lib',
    'passlib',
    'argon2_cffi',
    'translitcodec',
    'yappi'
  ],
  description='The Temboz RSS/Atom feed reader and aggregator.',
  classifiers=[
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
  ],
)
