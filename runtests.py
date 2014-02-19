#!/usr/bin/env python
import os
import sys
import pytest
import coverage

if __name__ == '__main__':
    # Environment variables
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

    # Start coverage tracking
    cov = coverage.coverage()
    cov.start()

    # Run pytest
    if len(sys.argv) > 1:
        pytest.main(sys.argv)
    else:
        pytest.main(['tests'])

    # Show coverage report
    cov.stop()
    cov.save()
    cov.report()
