ARG QGIS_TEST_VERSION=latest
FROM  qgis/qgis:${QGIS_TEST_VERSION}
MAINTAINER Denis Rouzaud <denis@opengis.ch>

RUN pip3 install pytest

