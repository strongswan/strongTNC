#!/usr/bin/env python
import os
import sys
import pytest

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    if len(sys.argv) > 1:
        pytest.main(sys.argv)
    else:
        pytest.main(['tests'])
