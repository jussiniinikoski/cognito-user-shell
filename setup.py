import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cognito-user-shell",  # Replace with your own username
    version="0.1.1",
    author="Jussi Niinikoski",
    author_email="jussi.niinikoski@perjantai.fi",
    description="Extendable shell/CLI tool with AWS Cognito authentication.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jussiniinikoski/cognito-user-shell",
    packages=setuptools.find_packages(exclude=["tests", "example"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)