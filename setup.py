from setuptools import setup, find_packages


def read(fname):
    with open(fname) as fp:
        return fp.read().split('\n\n\n')[0]

setup(
    name='pyclts',
    version="1.0.0",
    description='A python library to check phonetic transcriptions',
    long_description=read("README.md"),
    author='Johann-Mattis List',
    author_email='mattis.list@lingpy.org',
    url='https://github.com/glottobank/cpa',
    install_requires=[
        'attrs',
        'clldutils>=1.13.6',
    ],
    include_package_data=True,
    license="GPL",
    zip_safe=False,
    keywords='',
    classifiers=[
        ],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'clts=pyclts.cli:main',
        ]
    },
    tests_require=['nose', 'coverage', 'mock'],
)
