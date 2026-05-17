#!/bin/bash

PROJECT_DIR="/Users/aswin.m/Desktop/auto-trade-options"

LOG_DIR="$PROJECT_DIR/logs"

mkdir -p "$LOG_DIR"

TIMESTAMP=$(date +"%Y_%m_%d_%H_%M_%S")

LOG_FILE="$LOG_DIR/bot_$TIMESTAMP.log"

cd "$PROJECT_DIR"


python main.py >> "$LOG_FILE" 2>&1