#!/bin/sh
cd gauge-proto
protoc --python_out=../getgauge/messages/ spec.proto
protoc --python_out=../getgauge/messages/ messages.proto
