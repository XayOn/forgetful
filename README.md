# forgetful_esp32

[![PyPI - Version](https://img.shields.io/pypi/v/forgetful-esp32.svg)](https://pypi.org/project/forgetful-esp32)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/forgetful-esp32.svg)](https://pypi.org/project/forgetful-esp32)

-----

**Table of Contents**

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install forgetful-esp32
```

## License

`forgetful-esp32` is distributed under the terms of the [GPL-3.0](https://spdx.org/licenses/GPL-3.0.html) license.


## Post-installation

You'd need yolov8n model, download it with:

hatch run yolo task=detect mode=export model=yolov8n.pt format=onnx opset=13
