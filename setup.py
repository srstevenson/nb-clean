"""Setup module for nb-clean."""

from pathlib import Path

from setuptools import setup


def read_long_description():
    """Read from README.rst file in root of source directory."""
    root = Path(__file__).resolve().parent
    readme = root / 'README.rst'
    return readme.read_text()


setup(
    name='nb-clean',
    version='1.0.1',
    description='Clean Jupyter notebooks for versioning',
    long_description=read_long_description(),
    url='https://github.com/srstevenson/nb-clean',
    author='Scott Stevenson',
    author_email='scott@stevenson.io',
    license='ISC',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3.6',
    ],
    scripts=['nb-clean'],
    install_requires=['nbformat'],
    keywords='jupyter notebook git filter'
)
