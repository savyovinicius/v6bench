#!/bin/sh

SCRIPT_PATH="$(dirname "$(realpath "$0")")"
KATHARA_PATH="${SCRIPT_PATH}/kathara/"

# checking if lab still exists and cleans if needed
if ! (kathara linfo -d "${KATHARA_PATH}" |grep -Fq "No Devices Found"); then
    kathara lclean -d "${KATHARA_PATH}"
fi

echo "Starting Tests"
sudo kathara lstart --noterminals -d "${KATHARA_PATH}"

while [ "$(kathara linfo -d "${KATHARA_PATH}" |grep -Fq 'running')" -ne 0 ]; do
    echo "Tests still running. Checking again in 10 seconds"
    sleep 10
done

echo "Tests are now completed. Cleaning environment"
kathara lclean -d "${KATHARA_PATH}"
echo "Done"