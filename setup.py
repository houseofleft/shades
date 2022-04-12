from setuptools import setup, find_packages

with open("README.md", "r") as file:
    long_description = file.read()

setup(
    name='shades',
    version='1.0',
    author='Ben Rutter',
    description='A Python module for generative 2d image creation',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/benrrutter/shades',
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=[
        'numpy>=1.20.0',
        'Pillow>=8.0.0',
    ]
) 
