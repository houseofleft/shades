from setuptools import setup, find_packages

with open("README.md", "r") as file:
    long_description = file.read()

setup(
    name='shades',
    version='0.1.1',
    author='Ben Rutter',
    description='A Python module for generative 2d image creation',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/benrrutter/shades',
    packages=find_packages(),
    python_requires='>=3.6',
) 
