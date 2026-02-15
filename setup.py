from setuptools import setup, find_packages

setup(
    name="kernhell",
    version="0.2",
    packages=[
        'kernhell',
        'kernhell.core',
        'kernhell.strategies',
        'kernhell.strategies.web',
        'kernhell.strategies.python',
        'kernhell.strategies.mobile',
        'kernhell.strategies.native',
    ],
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
            "kernhell=kernhell.core.main:app",
        ],
    },
)