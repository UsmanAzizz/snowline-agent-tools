from setuptools import setup, find_packages

setup(
    name="snowline-agent-tools",
    version="1.0.3",
    description="Portable agent tools for coding assistants.",
    packages=find_packages(),
    include_package_data=True,
    package_data={"snowline_toolkit": ["py.typed"]},
)
