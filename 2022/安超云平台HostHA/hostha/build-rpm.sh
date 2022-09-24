#!/bin/bash
set -e
set -x

rm -rf rpmbuild/SOURCES
mkdir -p rpmbuild/SOURCES
python setup.py -q sdist --dist-dir rpmbuild/SOURCES

export CU_VERSION=`ls -r rpmbuild/SOURCES | head -1 | awk -F '-' '{print $2}' | awk -F '.tar.gz' '{print $1}'`
export TOPDIR=`pwd`/rpmbuild

rpmbuild -bb --define "_topdir $TOPDIR" \
  --define "version $CU_VERSION" \
  package/hostha.spec
