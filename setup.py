from setuptools import setup, find_packages

setup(
    name='reactive-pydantic',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A library for creating reactive Pydantic models using RxPy.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/reactive-pydantic',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'pydantic>=1.0.0',
        'rx>=3.0.0'
    ],
    extras_require={
        'dev': [
            'pytest',
            'black',
            'mypy',
            'flake8'
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)