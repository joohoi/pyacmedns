import os
from setuptools import setup, find_packages

def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

install_requires = [
    'requests',
]

setup(
    name='pyacmedns',
    version="0.4",
    description=("Library that implements the acme-dns client communication and "
                 "persistent account storage on the client host"),
    long_description=read('README.rst'),
    long_description_content_type='text/x-rst',
    url='https://github.com/joohoi/pyacmedns',
    download_url='https://github.com/joohoi/pyacmedns/archive/0.4.tar.gz',
    author="Joona Hoikkala",
    author_email='joona@kuori.org',
    license="MIT",
    packages=find_packages(),
    install_requires=install_requires,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
    ],
    keywords=['acme tls x509 acmedns letsencrypt'],
)
