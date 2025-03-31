from setuptools import setup, find_packages

setup(
    name="bvista",
    version="0.1.0",
    author="Bassey Akom",
    author_email="bassi.cim@gmail.com",
    description="B-Vista: A powerful data visualization and exploration tool",
    packages=find_packages(include=["bvista", "bvista.*", "datasets", "datasets.*"]),
    install_requires=[
        "flask",
        "flask-socketio",
        "flask-cors",
        "pandas",
        "numpy",
        "requests"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
