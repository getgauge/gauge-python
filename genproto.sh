#!/bin/sh
cd gauge-proto
protoc --python_out=../gauge/messages/ spec.proto
protoc --python_out=../gauge/messages/ messages.proto
protoc --python_out=../gauge/messages/ api.proto
