from setuptools import setup, find_packages

VERSION = '0.0.2'


setup(
    name="mkdocs-bootstrap386",
    version=VERSION,
    url='https://gitlab.com/lramage94/mkdocs-bootstrap386',
    license='BSD',
    description='A vintage 1980s DOS inspired Twitter Bootstrap theme for MkDocs',
    author='Lucas Ramage',
    author_email='ramage.lucas@protonmail.com',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'mkdocs.themes': [
            'bootstrap386 = mkdocs_bootstrap386',
        ]
    },
    zip_safe=False
)
