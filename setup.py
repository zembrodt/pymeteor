import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pymeteor",
    version="0.0.2b",
    author="Ryan Zembrodt",
    author_email="ryan.zembrodt@uky.edu",
    description="Python implementation of METEOR",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zembrodt/pymeteor",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)