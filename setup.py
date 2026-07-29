from setuptools import setup, find_packages
import os

setup(
    name="snowline-agent-tools",
    version="1.0.1",
    description="Simple, portable Python scripts to guide AI coding assistants.",
    author="UsmanAzizz",
    packages=find_packages(),
    include_package_data=True,
    data_files=[
        ('scripts', ['scripts/snowline.bat']),
    ],
    entry_points={
        'console_scripts': [
            'snowline=snowline_toolkit.cli:main',
        ],
    },
    python_requires=">=3.7",
)
