# setup.py

from setuptools import setup, find_packages

setup(
    name="pusheraio",  
    version="0.3",
    packages=find_packages(),
    install_requires=[
        "pusher",
        "websocket-client"
    ],
    description="All in one pusher library.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Ehan Chowdhury",
    author_email="nibizsoft@gmail.com",
    url="https://github.com/EhanChowdhury/pusheraio",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
