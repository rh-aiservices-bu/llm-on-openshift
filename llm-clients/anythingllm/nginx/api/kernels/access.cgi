#!/bin/bash
echo "Status: 200"
echo "Content-type: application/json"
echo
# Retrieve last line from custom logs
LOG_TAIL=$(tail -n 1 /var/log/nginx/anythingllm.access.log)
# Extract last_activity field
LAST_ACTIVITY=$(echo $LOG_TAIL | grep -Po 'last_activity":"\K.*?(?=")')
if [[ $(date -d $LAST_ACTIVITY"+10 minutes" +%s) -lt $(date +%s) ]]; then
    # No activity for the past 10mn, we consider code-server idle and begin to send idle response
    # As logs always write "busy", we first substitute with "idle" in the answer
    sed s/busy/idle/ <<<"$LOG_TAIL"
else
    echo $LOG_TAIL
fi