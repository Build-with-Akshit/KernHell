from setuptools import setup, find_packages

setup(
    name="kernhell",
    version="0.2",
    packages=find_packages(),
    install_requires=[
        "typer[all]",
        "rich",
        "playwright",
        "google-generativeai",
        "groq",
        "pytest"
    ],
    entry_points={
        "console_scripts": [
            "kernhell=kernhell.main:app",
        ],
    },
)