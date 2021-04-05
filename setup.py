import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

reqs = ["flask>=1.1.2", "phonenumbers>=8.12.20", "flask-limiter>=1.4", "redis>=3.5.3"]

setuptools.setup(
    name="phonecheck",  # Replace with your own username
    version="0.0.2",
    author="Example Author",
    author_email="author@example.com",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    project_urls={
        "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    package_data={
        "phonecheck": ["templates/*"],
    },
    packages=setuptools.find_packages(exclude=["test"]),
    python_requires=">=3.6",
    install_requires=reqs,
)
