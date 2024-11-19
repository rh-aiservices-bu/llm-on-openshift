#!/bin/bash
source ./cpu/.venv/bin/activate
watchmedo auto-restart --pattern "*.py" --recursive --signal SIGTERM python common/app.py