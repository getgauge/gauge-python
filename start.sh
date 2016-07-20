#!/usr/bin/env bash
if [ -z "$GAUGE_PYTHON_COMMAND" ]; then
  GAUGE_PYTHON_COMMAND="python"
fi

${GAUGE_PYTHON_COMMAND} -u start.py $1