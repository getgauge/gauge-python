from distutils.core import setup
from datetime import date

setup(
    name='getgauge-nightly',
    packages=['getgauge', 'getgauge/messages'],
    version=str(date.today()).replace('-', '.'),
    description='Enables Python support for Gauge',
    author='Gauge Team',
    author_email='getgauge@outlook.com',
    url='https://github.com/getgauge/gauge-python',
    keywords=['testing', 'gauge', 'gauge-python', 'getgauge', 'automation'],
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=['protobuf==3.3.0', 'redBaron', 'colorama'],
)
