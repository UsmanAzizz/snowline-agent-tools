from setuptools import setup, find_packages

setup(
    name="snowline-agent-tools",
    version="1.0.0",
    description="Simple, portable Python scripts to guide AI coding assistants.",
    author="UsmanAzizz",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "snowline-init=snowline_toolkit.cli:main",
        ],
    },
    python_requires=">=3.7",
)
