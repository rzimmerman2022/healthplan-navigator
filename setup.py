from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="healthplan-navigator",
    version="1.1.2",
    author="Ryan Zimmerman",
    author_email="rzimmerman2022@example.com",
    description="AI-powered healthcare plan analysis system with 6-metric scoring",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rzimmerman2022/healthplan-navigator",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Healthcare Industry",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pdfplumber>=0.9.0",
        "python-docx>=0.8.11",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "plotly>=5.15.0",
        "pathlib2>=2.3.7",
    ],
    entry_points={
        "console_scripts": [
            "healthplan-navigator=healthplan_navigator.cli:main",
            "healthplan-demo=healthplan_navigator.analyzer:demo_main",
        ],
    },
    include_package_data=True,
    package_data={
        "healthplan_navigator": ["data/*.json"],
    },
)