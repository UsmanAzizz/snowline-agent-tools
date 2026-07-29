from setuptools import setup, find_packages

setup(
    name="snowline-agent-tools",
    version="1.0.5",
    description="Portable agent tools for coding assistants.",
    author="UsmanAzizz",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "snowline=snowline_toolkit.cli:main",
        ],
    },
    package_data={"snowline_toolkit": ["py.typed", "snowline.bat", "templates/**/*"]},
    python_requires=">=3.7",
)
