"""Setup script for PyBalance."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name='pybalance',
    version='2.0.0',
    author='Onur Mert Çeldir',
    author_email='onurceldir123@gmail.com',
    description='A Python package for assembly line balancing and optimization',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/onurceldir123/montage-line-balancing-module',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Manufacturing',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.7',
    install_requires=[
        'networkx>=2.5',
        'numpy>=1.19.0',
        'matplotlib>=3.3.0',
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.10',
            'black>=21.0',
            'flake8>=3.8',
            'mypy>=0.900',
        ],
    },
    keywords='assembly line balancing, optimization, manufacturing, operations research',
    project_urls={
        'Bug Reports': 'https://github.com/onurceldir123/montage-line-balancing-module/issues',
        'Source': 'https://github.com/onurceldir123/montage-line-balancing-module',
        'Documentation': 'https://github.com/onurceldir123/montage-line-balancing-module/blob/main/Guide.pdf',
    },
)
