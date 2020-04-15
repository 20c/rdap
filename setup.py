from setuptools import find_packages, setup


def read_file(name):
    with open(name) as fobj:
        return fobj.read().strip()


LONG_DESCRIPTION = read_file("README.md")
VERSION = read_file("Ctl/VERSION")
REQUIREMENTS = read_file("Ctl/requirements.txt").split("\n")
TEST_REQUIREMENTS = read_file("Ctl/requirements-test.txt").split("\n")


setup(
    name="rdap",
    version=VERSION,
    author="20C",
    author_email="code@20c.com",
    description="Registration Data Access Protocol tools",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    license="LICENSE",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries",
    ],
    packages=find_packages(),
    include_package_data=True,
    url="https://github.com/20c/rdap",
    download_url="https://github.com/20c/rdap/archive/{}.zip".format(VERSION),
    install_requires=REQUIREMENTS,
    test_requires=TEST_REQUIREMENTS,
    entry_points={"console_scripts": ["rdap=rdap.__main__:main",]},
    zip_safe=True,
)
