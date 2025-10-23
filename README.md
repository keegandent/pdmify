<!--
 Copyright (c) 2025 Keegan Dent

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at https://mozilla.org/MPL/2.0/.
-->

# pdmify

## Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Usage](#usage)

## About <a name = "about"></a>

Convert PCM audio files to PDM

## Getting Started <a name = "getting_started"></a>

Clone this repository and `cd` into it.

```bash
git clone git@github.com:keegandent/pdmify.git
cd pdmify/
```

### Python Environment

Create a virtual environment, then activate it.

```bash
python -m venv venv
source venv/bin/activate
```

Install this project and dependencies using pip like so.

```bash
python -m pip install -e .[dev,test]
```

If you want to use GPU acceleration, you're responsible for installing a CuPy compatible with your version of CUDA. FOr example, on my machine:

```sh
sudo apt install nvidia-cuda-toolkit
# above installed CUDA Toolkit 11.5
pip install cupy-cuda11x
```

## Usage <a name = "usage"></a>

### Scripts

```bash
pdmify -h
```
