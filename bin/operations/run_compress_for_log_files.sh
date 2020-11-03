#!/bin/bash

#######################################
CURRENT=$(cd $(dirname $0) && pwd)
PROJECT_ROOT="$(cd ${CURRENT%/}/../../ && pwd)"
BIN="${PROJECT_ROOT}/bin"

. ${BIN}/common.sh

LOG_RETENTION_PERIOD=3
#######################################

find ${LOGS} -type f -mtime +${LOG_RETENTION_PERIOD} -name '*.log.*' ! -name '*.gz' | xargs --no-run-if-empty gzip
