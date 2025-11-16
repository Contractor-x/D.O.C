from setuptools import setup, find_packages

setup(
    name="doc-backend",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "pydantic",
        "supabase",
        "python-jose",
        "passlib",
    ],
    extras_require={
        "dev": [
            "pytest",
            "black",
            "isort",
            "flake8",
            "mypy",
        ],
    },
)
