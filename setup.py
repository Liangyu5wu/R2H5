from setuptools import setup, find_packages

setup(
    name='r2h5',
    version='1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'r2h5=r2h5.cli:main',
        ],
    },
    install_requires=[
        'numpy',
        "h5py",
        "pyyaml",
        "uproot"
    ],
)

