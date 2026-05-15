#!/bin/bash
killall uvicorn 2>/dev/null
.venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload 2> server.log &
