# Installation Guide

`djicot` is a command-line program that provides various functionalities. Below are the methods to install DJICOT, listed by complexity.

## Debian, Ubuntu, Raspberry Pi

To install `djicot` and its prerequisite package [PyTAK](https://pytak.rtfd.io), follow these steps:

```sh linenums="1"
sudo apt update -qq
wget https://github.com/snstac/aircot/releases/latest/download/aircot_latest_all.deb
sudo apt install -f ./pytak_latest_all.deb
wget https://github.com/snstac/djicot/releases/latest/download/djicot_latest_all.deb
sudo apt install -f ./djicot_latest_all.deb
```

## Windows, Linux

For advanced users, install `djicot` from the Python Package Index (PyPI):

```sh
sudo python3 -m pip install djicot
```

## Developers

We welcome pull requests! To set up a development environment, use the following commands:

```sh linenums="1"
git clone https://github.com/snstac/djicot.git
cd djicot/
python3 setup.py install
```
