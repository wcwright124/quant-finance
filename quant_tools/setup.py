from setuptools import setup

setup(
    name='quant_tools',
    version='0.0.1',
    description='A collection of tools for algorithmic trading.',
    author='Will Wright',
    install_requires=[
        'bs4',
        'datetime',
        'json',
        'MySQLdb',
        'pandas',
        'requests'
        ]
)