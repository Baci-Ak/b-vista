from setuptools import setup, find_packages

setup(
    name="bvista",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="B-Vista: A powerful data visualization and exploration tool",
    packages=find_packages(),
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
