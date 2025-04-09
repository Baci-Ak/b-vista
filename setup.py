from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bvista",
    version="0.1.17",
    author="Bassey Akom",
    author_email="bassi.cim@gmail.com",
    description="B-Vista: A powerful data visualization and exploration tool for pandas DataFrames.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Baci-Ak/b-vista",
    packages=find_packages(
        include=["bvista", "bvista.*", "backend", "backend.*"]
    ),
    include_package_data=True,
    install_requires=[
        "flask>=2.0.0",
        "flask-socketio>=5.0.0",
        "flask-cors",
        "pandas>=1.0",
        "numpy>=1.18",
        "requests",
        "matplotlib",
        "seaborn",
        "plotly",
        "missingno",
        "scikit-learn",
        "statsmodels",
        "ipywidgets",  # required for notebook interaction
         "dcor", 
         "pymc",
         "pingouin",

    ],
    classifiers=[
        "Development Status :: 4 - Beta",  # change when you're ready!
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    python_requires=">=3.7",
    project_urls={
        "Documentation": "https://github.com/Baci-Ak/b-vista#readme",
        "Source": "https://github.com/Baci-Ak/b-vista",
        "Bug Tracker": "https://github.com/Baci-Ak/b-vista/issues",
    },
)
