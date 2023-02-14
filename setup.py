import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cognito-user-shell",  # Replace with your own username
    version="0.1.8",
    author="Jussi Niinikoski",
    author_email="jussi.niinikoski@perjantai.fi",
    description="Extendable shell/CLI tool with AWS Cognito authentication.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jussiniinikoski/cognito-user-shell",
    packages=[
        "cognito_user_shell",
    ],
    install_requires=[
        "boto3",
        "requests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
