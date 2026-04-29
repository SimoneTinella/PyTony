from pathlib import Path

from setuptools import setup


ROOT = Path(__file__).parent


setup(
    name="pytony",
    version="0.1.0",
    description="Pytony: un linguaggio ironico costruito sopra Python.",
    long_description=(ROOT / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    author="Simone Tinella",
    python_requires=">=3.11",
    packages=["pytony"],
    entry_points={
        "console_scripts": [
            "pytony=pytony.cli:main",
        ]
    },
)
