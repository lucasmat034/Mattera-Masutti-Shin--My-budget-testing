from setuptools import setup, find_packages

setup(
    name="mybudget",
    version="1.0.0",
    description="Application de gestion de budget personnel",
    author="Votre Groupe",
    author_email="rida@lamerkanterie.fr",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click>=8.1.0',
        'tabulate>=0.9.0',
        'python-dateutil>=2.8.2',
    ],
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-cov>=4.1.0',
            'pytest-bdd>=6.1.1',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.0.0',
        ]
    },
    entry_points={
        'console_scripts': [
            'mybudget=src.cli.main:cli',
        ],
    },
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
