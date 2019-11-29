#!/bin/sh

if [ -z "$GAUGE_PYTHON_COMMAND" ]; then
  GAUGE_PYTHON_COMMAND="python"
fi

${GAUGE_PYTHON_COMMAND} -m grpc_tools.protoc -I gauge-proto --python_out=getgauge/messages --grpc_python_out=getgauge/messages gauge-proto/*.proto
# git clean -fx
warning="Please update the import staement \n\t'import spec_pb2 as spec__pb2'\n to \n\t'import getgauge.messages.spec_pb2 as spec__pb2'\nin following files -\n\tmessages_pb2.py\n\tlsp_pb2.py\n\tapi_pb2.py
\n\nTHIS IS DONE IN ORDER TO ADDRESS RELATIVE IMPORT ISSUE IN DIFFERENT PYTHON VERSIONS."
echo $warning