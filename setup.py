from setuptools import setup, find_packages
from setuptools.command.install import install


class PostInstallMessage(install):
    """Print a short welcome message after installation completes."""
    def run(self):
        install.run(self)
        print()
        print("=" * 50)
        print("  Snowline Agent Tools installed")
        print("=" * 50)
        print("Next step:")
        print("  snowline init --apply")
        print("  (or: python -m snowline.cli init --apply)")
        print()
        print("This creates .agents/ in your project with:")
        print("  - 14 tools + companion intent analyzer")
        print("  - agents.md (behavior rules read by your AI agent)")
        print()


setup(
    name="snowline-agent-tools",
    version="1.0.6",
    description="Portable agent tools for coding assistants.",
    author="UsmanAzizz",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "snowline=snowline.cli:main",
        ],
    },
    package_data={"snowline": ["py.typed", "snowline.bat", "templates/**/*"]},
    python_requires=">=3.7",
    cmdclass={"install": PostInstallMessage},
)
