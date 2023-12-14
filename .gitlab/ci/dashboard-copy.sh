#!/bin/sh
if [ "${CI_DEBUG_TRACE}" = "true" ]; then
    set -x
fi

set -euo pipefail
IFS=$'\n\t'

print_usage() {
    echo "Copy a local file to a remote directory on dashboard, remote directory"
    echo "is created if missing."
    echo ""
    echo "Usage:"
    echo "  dashboard-copy.sh <src> <dstdir>"
    echo ""
    echo "Environment:"
    echo "  DASHBOARD_HOST         Dashboard host (default: intranet.aresys.it)"
    echo "  DASHBOARD_USER_LOGIN   User login (default: sardashboard)"
    echo "  DASHBOARD_PORT         TCP port number (default: 22)"
    echo "  DASHBOARD_PRIVATE_KEY  Login private key (required)"
    echo ""
}

# parse command line arguments
if [ $# -ne 2 ]; then
    print_usage
    exit 1
fi
SRC=$1
DSTDIR=$2

# check environment variables
if [ -z "${DASHBOARD_PRIVATE_KEY+x}" ]; then
    echo "Missing dashboard private key"
    exit 1
fi

if [ -z "${DASHBOARD_USER_LOGIN+x}" ]; then
    DASHBOARD_USER_LOGIN=sardashboard
fi

if [ -z "${DASHBOARD_HOST+x}" ]; then
    DASHBOARD_HOST=intranet.aresys.it
fi

if [ -z "${DASHBOARD_PORT+x}" ]; then
    DASHBOARD_PORT=22
fi

cat "$DASHBOARD_PRIVATE_KEY" | base64 -d | ssh-add -
ssh-keyscan -H $DASHBOARD_HOST >> ~/.ssh/known_hosts
ssh -p $DASHBOARD_PORT \
    -l $DASHBOARD_USER_LOGIN \
    $DASHBOARD_HOST \
    mkdir -pv $DSTDIR
rsync --port=$DASHBOARD_PORT \
      --compress \
      --stats \
      $SRC $DASHBOARD_USER_LOGIN@$DASHBOARD_HOST:$DSTDIR
