import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name='temboz',
  author='Fazal Majid',
  author_email='python@sentfrom.com',
  version='4.5.5',
  url='https://github.com/fazalmajid/temboz',
  #package_dir={'': 'src'},
  packages=['tembozapp'] + setuptools.find_packages(),
  include_package_data=True,
  scripts=['temboz'],
  install_requires=[
    'flask',
    'requests',
    'html5lib>=1.1',
    'passlib',
    'argon2_cffi',
    'ctranslitcodec',
    'sgmllib3k',
    'feedparser>=6.0.2',
    'werkzeug>=1.0.1',
    'bleach>=3.2.1',
    'yappi'
  ],
  description='The Temboz RSS/Atom feed reader and aggregator.',
  long_description=long_description,
  long_description_content_type='text/markdown',
  classifiers=[
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
  ],
)
