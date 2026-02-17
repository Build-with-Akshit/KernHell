from setuptools import setup, find_packages

setup(
    name="kernhell",
    version="2.0",
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
        "openai",
        "requests",
        "pytest",
        "Pillow>=10.0.0",
        "watchdog>=3.0.0",
        "jinja2>=3.1.0",
    ],
    extras_require={
        "semantic": [
            "chromadb>=0.4.0",
            "sentence-transformers>=2.2.0",
            "beautifulsoup4>=4.12.0",
        ],
        "alerts": [
            "slack-sdk>=3.23.0",
            "twilio>=8.10.0",
        ],
        "full": [
            "chromadb>=0.4.0",
            "sentence-transformers>=2.2.0",
            "beautifulsoup4>=4.12.0",
            "slack-sdk>=3.23.0",
            "twilio>=8.10.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "kernhell=kernhell.core.main:app",
        ],
    },
)
