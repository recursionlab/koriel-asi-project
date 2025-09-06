#!/bin/bash
# Minimal nondeterminism bisector - Item 6
# Find the first bad seed that causes test failures

set -e
lo=1
hi=1000

bad() {
    SEED=$1 python -m pytest -q >/dev/null 2>&1 || return 0
    return 1
}

while [ $lo -lt $hi ]; do
    mid=$(( (lo+hi)/2 ))
    if bad $mid; then
        hi=$mid
    else
        lo=$((mid+1))
    fi
done

echo "first-bad-seed:$lo"