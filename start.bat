@echo off
IF "%GAUGE_PYTHON_COMMAND%"=="" (SET GAUGE_PYTHON_COMMAND="python")
%GAUGE_PYTHON_COMMAND% check_and_install_getgauge.py
%GAUGE_PYTHON_COMMAND% -u start.py %1
