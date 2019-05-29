from setuptools import setup, find_packages

setup(
    name='harbinger',
    version='0.0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'harbinger = harbinger.cli.main:main',
        ],
    },
    install_requires=[
        'pyyaml',
        'github3.py'
    ],
    extras_require={
        'test': [
            'pytest',
        ],
    }
)
