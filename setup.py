import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pie-manager",
    version="1.0.4.3",
    author="Terroid",
    author_email="skandabhairava@gmail.com",
    description="A very loose and easy to use project manager",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/skandabhairava/Pie-manager",
    entry_points={
        "console_scripts": ["pie=pie_manager.cli:entry_point"],
    },
    project_urls={
        "Bug Tracker": "https://github.com/skandabhairava/Pie-manager/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)