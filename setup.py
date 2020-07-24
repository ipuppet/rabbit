import setuptools

with open("README.md", "r") as f:
    long_description = f.read()
    setuptools.setup(
        name="rabbit",
        version="0.0.1",
        author="ipuppet",
        author_email="zimingw.ol@outlook.com",
        description="A personal cloud service management system",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="",
        packages=setuptools.find_packages(),
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
    )
    f.close()
