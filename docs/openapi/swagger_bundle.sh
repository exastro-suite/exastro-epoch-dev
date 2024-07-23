#!/bin/sh
BASEDIR=$(dirname "$0")

swagger-cli bundle -o ${BASEDIR}/build/openapi.yaml -t yaml ${BASEDIR}/openapi.yaml
swagger-cli bundle -o ${BASEDIR}/build/user_reference.yaml -t yaml ${BASEDIR}/user_reference.yaml
