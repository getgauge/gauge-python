#!/usr/bin/env bash
set -e

if [ -z "$GAUGE_PYTHON_COMMAND" ]; then
  GAUGE_PYTHON_COMMAND="python"
fi

# Resolve relative paths against the project root
case "$GAUGE_PYTHON_COMMAND" in
  /* ) ;;
  */* )
    if [ -n "$GAUGE_PROJECT_ROOT" ]; then
      GAUGE_PYTHON_COMMAND="$GAUGE_PROJECT_ROOT/$GAUGE_PYTHON_COMMAND"
    fi
    ;;
esac

${GAUGE_PYTHON_COMMAND} check_and_install_getgauge.py

${GAUGE_PYTHON_COMMAND} -u start.py $1