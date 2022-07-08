# Debian/Ubuntu (`apt`) Installation

## Install `python3.10` or `python3.11`

Execute lines 1 at a time.

```bash
# Update packages
sudo apt update && sudo apt upgrade -y

# For adding custom PPAs
sudo apt install software-properties-common -y

# Add PPA, then press [ENTER]
sudo add-apt-repository ppa:deadsnakes/ppa

# Install 'python3.10'
sudo apt install python3.10

# Install 'python3.10 -m pip'
curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3.10
```

## Install `pip` package `rdfhash`

```bash
python3.10 -m pip install rdfhash
```

## Test Script

```bash
rdfhash -d '[ a <def:class:Person> ] .' -m 'blake2b'
```

```bash
<blake2b:62f6085cfe85339cd98681823db5e107f2d24beaaeb8a41484f278135701886edbb28e0628a4039a3efdca116a448dee1dc2afccdda79ef87de6551b0367c795> a <def:class:Person> .
```
