#!/usr/bin/env python3
import os
import sys
import pytest
import coverage
from django.test import TransactionTestCase

TransactionTestCase.databases = {'default', 'meta'}

if __name__ == '__main__':
    # Environment variables
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_tests')

    measure_coverage = True
    if '--no-cov' in sys.argv:
        measure_coverage = False
        sys.argv.remove('--no-cov')

    # Start coverage tracking
    if measure_coverage:
        cov = coverage.coverage()
        cov.start()

    # Run pytest
    if len(sys.argv) > 1:
        code = pytest.main(sys.argv)
    else:
        code = pytest.main(['tests', 'apps'])

    # Show coverage report
    if measure_coverage:
        cov.stop()
        cov.save()
        cov.report()

    sys.exit(code)
