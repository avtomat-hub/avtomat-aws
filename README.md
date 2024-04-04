<div align="center">
  <center>
    <a href="https://github.com/avtomat-hub/avtomat-aws">
      <img width="350" alt="Avtomat logo" src="logo.svg" />
    </a>
  </center>
</div>
<div align="center" style="margin-top: -30px">
  <center><h1 align="center">Automate Cloud Operations, AWS Collection<i></i></h1></center>
  <center><h4>Maintained by <a style="color: #2d547d;" href="https://avtomat.io" target="_blank">Avtomat</a></h4><i></i></center>
</div>

<div align="center">

[![homepage](https://img.shields.io/website?url=https%3A%2F%2Favtomat.io&style=flat-square)](https://avtomat.io)
[![documentation](https://img.shields.io/badge/documentation-yes-brightgreen.svg?style=flat-square)](https://docs.avtomat.io/aws/get_started)
[![contributing](https://img.shields.io/badge/contributing-guide-blue?style=flat-square)](/docs/CONTRIBUTING.md)
<br/>
[![version](https://img.shields.io/pypi/v/avtomat-aws?style=flat-square&label=version&color=blue)](https://github.com/avtomat-hub/avtomat-aws)
[![build](https://img.shields.io/github/actions/workflow/status/avtomat-hub/avtomat-aws/publish-to-pypi.yml?style=flat-square)](https://github.com/avtomat-hub/avtomat-aws/actions/workflows/publish-to-pypi.yml)
[![python](https://img.shields.io/pypi/pyversions/avtomat-aws?style=flat-square)](https://pypi.org/p/avtomat-aws)
[![status](https://img.shields.io/pypi/status/avtomat-aws?style=flat-square)](https://pypi.org/p/avtomat-aws)
[![license](https://img.shields.io/github/license/avtomat-hub/avtomat-aws?style=flat-square)](https://github.com/avtomat-hub/avtomat-aws/blob/main/LICENSE)

</div>

> </br><h4 align="center">**A Python collection of Amazon Web Services actions. </br> 
> Built on top of Boto3.**</h4></br>

---

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
  - [PyPi](#pypi)
- [Requirements](#requirements)
- [Contributing](#contributing)
  - [Affiliates](#affiliates)
- [License](#license)

---

## Overview

This repository is home to the Avtomat AWS collection. It includes pre-defined actions for automating cloud operations on Amazon Web Services. </br> 
The actions are written in Python and can be used as standalone scripts or incorporated into your own projects. </br> 
Additionally, the entire collection has a CLI interface, providing easy access to actions. </br> </br>
For a list of available actions or usage instructions, see the [documentation](https://docs.avtomat.io/aws/get_started).

---

## Installation

Currently, this collection can only be installed from PyPi.

### PyPi

If you already have Python3 and pip3 installed, you can perform:

#### Virtual Environment Installation (pip)

```shell 
python3 -m venv venv
source venv/bin/activate
pip install avtomat-aws
aaws --help
```

#### System-wide Installation (recommended: pipx)

```shell
pipx install avtomat-aws
aaws --help
```

## Requirements

To run this collection, you only need [Python3](https://www.python.org/) and [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html).

---

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/avtomat-hub/avtomat-aws/issues). <br>If you are interested in contributing or would like to make some modifications, please take a look at the [contributing guide](/docs/CONTRIBUTING.md).

---

## License

Copyright © 2024 [Avtomat Ltd](https://avtomat.io). This project is [GPLv2](https://github.com/avtomat-hub/avtomat-aws/blob/main/LICENSE) licensed.