#!/usr/bin/env python3
"""
Setup script for LinkAce Classifier package
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open(os.path.join(this_directory, 'requirements.txt'), encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="linkace-classifier",
    version="1.0.0",
    author="LinkAce Classifier Team",
    author_email="linkace-classifier@example.com",
    description="AI-powered URL classification for LinkAce",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alx/linkace-classifier",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "linkace-classifier=linkace_classifier.cli.main:main",
            "linkace-classifier-server=linkace_classifier.cli.server_main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "linkace_classifier": ["*.md", "*.txt"],
    },
    keywords="linkace, url, classification, ai, ollama, api",
    project_urls={
        "Bug Reports": "https://github.com/alx/linkace-classifier/issues",
        "Source": "https://github.com/alx/linkace-classifier",
        "Documentation": "https://github.com/alx/linkace-classifier/blob/main/docs/",
    },
)