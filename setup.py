from setuptools import setup, find_packages
import codecs

setup(
    name='pyclts',
    version="1.3.0",
    description='A python library to check phonetic transcriptions',
    long_description=codecs.open("README.md", 'r', 'utf-8').read(),
    long_description_content_type='text/markdown',
    author='Johann-Mattis List, Cormac Anderson, Tiago Tresoldi, Christoph Rzymski, Simon Greenhill, and Robert Forkel',
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
            'pytest>=3.6',
            'pytest-mock',
            'mock',
            'pytest-cov',
            'coverage>=4.2',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    license="GPL",
    zip_safe=False,
    keywords='',
    entry_points={
        'console_scripts': [
            'clts=pyclts.__main__:main',
        ]
    },
)
