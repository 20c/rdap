
from setuptools import find_packages, setup


version = open('facsimile/VERSION').read().strip()
requirements = open('facsimile/requirements.txt').read().split("\n")
test_requirements = open('facsimile/requirements-test.txt').read().split("\n")


setup(
    name='rdap',
    version=version,
    author='20C',
    author_email='code@20c.com',
    description='Registration Data Access Protocol tools',
    long_description='',
    license='LICENSE.txt',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
    ],
    packages = find_packages(),
    include_package_data=True,
    url='https://github.com/20c/rdap',
    download_url='https://github.com/20c/rdap/%s' % version,

    install_requires=requirements,
    test_requires=test_requirements,

    entry_points={
        'console_scripts': [
            'rdap=rdap.__main__:main',
        ]
    },

    zip_safe=True
)
