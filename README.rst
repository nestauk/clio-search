========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |appveyor| |requires|
        | |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|

.. |docs| image:: https://readthedocs.org/projects/python-clio/badge/?style=flat
    :target: https://readthedocs.org/projects/python-clio
    :alt: Documentation Status

.. |travis| image:: https://travis-ci.org/kstathou/python-clio.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/kstathou/python-clio

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/kstathou/python-clio?branch=master&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/kstathou/python-clio

.. |requires| image:: https://requires.io/github/kstathou/python-clio/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/kstathou/python-clio/requirements/?branch=master

.. |codecov| image:: https://codecov.io/github/kstathou/python-clio/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/kstathou/python-clio

.. |version| image:: https://img.shields.io/pypi/v/clio.svg
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/clio

.. |commits-since| image:: https://img.shields.io/github/commits-since/kstathou/python-clio/v0.1.0.svg
    :alt: Commits since latest release
    :target: https://github.com/kstathou/python-clio/compare/v0.1.0...master

.. |wheel| image:: https://img.shields.io/pypi/wheel/clio.svg
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/clio

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/clio.svg
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/clio

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/clio.svg
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/clio


.. end-badges

Text based information retrieval system

* Free software: BSD 2-Clause License

Installation
============

::

    pip install clio

Documentation
=============

https://python-clio.readthedocs.io/

Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
