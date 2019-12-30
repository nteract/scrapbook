#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

from mock import MagicMock
from ..utils import is_kernel


def test_is_kernel_true():
    class FakeIPyKernel:
        kernel = True

    sys.modules['IPython'] = MagicMock()
    sys.modules['IPython'].get_ipython.return_value = FakeIPyKernel
    assert is_kernel()
    del sys.modules['IPython']


def test_not_kernel_in_ipython():
    sys.modules['IPython'] = MagicMock()
    sys.modules['IPython'].get_ipython.return_value = {}
    assert not is_kernel()
    del sys.modules['IPython']
