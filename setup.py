import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name='temboz',
  author='Fazal Majid',
  author_email='python@sentfrom.com',
  version='4.0',
  url='https://github.com/fazalmajid/temboz',
  #package_dir={'': 'src'},
  packages=['tembozapp'] + setuptools.find_packages(),
  include_package_data=True,
  scripts=['temboz'],
  install_requires=[
    'flask',
    'requests',
    'html5lib',
    'passlib',
    'argon2_cffi',
    'ctranslitcodec',
    'feedparser',
    'werkzeug>=1.0.1',
    'bleach',
    'yappi'
  ],
  description='The Temboz RSS/Atom feed reader and aggregator.',
  long_description=long_description,
  long_description_content_type='text/markdown',
  classifiers=[
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.8',
  ],
)
