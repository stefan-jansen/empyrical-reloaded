#!/usr/bin/env python
#
# Copyright 2016 Quantopian, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import sys
from pathlib import Path
from setuptools import setup

# ensure the current directory is on sys.path
# so versioneer can be imported when pip uses
# PEP 517/518 build rules.
# https://github.com/python-versioneer/python-versioneer/issues/193
sys.path.append(Path(__file__).resolve(strict=True).parent.as_posix())
import versioneer  # noqa: E402

if __name__ == "__main__":
    setup(
        cmdclass=versioneer.get_cmdclass(),
        version=versioneer.get_version(),
        packages=["empyrical", "empyrical.tests"],
    )
