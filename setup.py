from setuptools import setup, find_packages
import codecs

setup(
    name='pyclts',
    version="1.0.0",
    description='A python library to check phonetic transcriptions',
    long_description=codecs.open("README.md", 'r', 'utf-8').read(),
    long_description_content_type='text/markdown',
    author='Johann-Mattis List, Tiago Tresoldi and Robert Forkel',
    author_email='mattis.list@lingpy.org',
    url='https://github.com/cldf/clts',
    install_requires=[
        'attrs>=18.2',
        'clldutils>=1.13.6',
        'csvw>=1.0',
        'uritemplate',
    ],
    extras_require={
        'dev': ['flake8', 'wheel', 'twine'],
        'test': [
            'pytest>=3.1',
            'pytest-mock',
            'mock',
            'pytest-cov',
            'coverage>=4.2',
        ],
    },
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    license="GPL",
    zip_safe=False,
    keywords='',
    classifiers=[
        ],
    entry_points={
        'console_scripts': [
            'clts=pyclts.__main__:main',
        ]
    },
)
