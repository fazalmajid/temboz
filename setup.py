import setuptools

setuptools.setup(
    name='temboz',
    author='Fazal Majid',
    author_email='python@sentfrom.com',
    version='2.0',
    url='http://github.com/fazalmajid/temboz',
    package_dir={'': 'src'},
    packages=['temboz'],
    description='The Temboz RSS/Atom feed reader and aggregator.',
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
    ],
)
