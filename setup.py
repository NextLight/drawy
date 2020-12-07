import setuptools

setuptools.setup(
    name="drawy",
    version="1.0.2",
    author="Samuele Turci",
    description="Easily create interactive graphical applications",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/NextLight/drawy",
    packages=setuptools.find_packages(),
    install_requires=[
        "skia-python==87.0",
        "glfw==2.0.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
