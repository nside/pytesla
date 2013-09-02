from distutils.core import setup

setup(
    name='pytesla',
    version='0.4',
    author='Denis Laprise',
    author_email='dlaprise@gmail.com',
    packages=['pytesla',],
    url='https://github.com/nside/pytesla',
    license='LICENSE.txt',
    description='Python bindings to the Model S REST API',
    long_description=open('README.rst').read(),
)
