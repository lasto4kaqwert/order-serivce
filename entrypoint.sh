#!/bin/sh
set -e

alembic upgrade head

python -u -m bin.outbox_worker &

exec "$@"