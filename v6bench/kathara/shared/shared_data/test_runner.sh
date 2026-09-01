#!/bin/sh

# shellcheck disable=SC1091
. /shared/env/credentials.env
. /shared/env/test_vars.env

pip install "curlify2<2.0.0,>=1.0.1" --break-system-packages --no-cache-dir # workarround for version compatibility issue with scanapi
pip install scanapi==2.13.2 --break-system-packages --no-cache-dir
HOSTNAME="$(/usr/bin/hostname)"


# waiting to SIIT to startup
if [ "${BASE_PROTO}" = "https" ]; then
    TEST_PORT=443
else
    TEST_PORT=80
fi

if timeout 60 sh -c "until nc -z 192.168.46.1 ${TEST_PORT}; do sleep 1; done"; then
    echo "SIIT server is up"
else
    echo "Timed out waiting for SIIT server" >&2
fi

# waiting to NAT64 to startup
if timeout 60 sh -c 'until ping -c 1 -W 1 64:ff9b::192.168.0.64 >/dev/null 2>&1; do sleep 1; done'; then
    echo "NAT64 server is up"
else
    echo "Timed out waiting for NAT64 server" >&2
fi


URL_TEMPLATE="lab.${BASE_DOMAIN}"
for sdom in ${SDOMS}; do
    BASE_URL="${BASE_PROTO}://${sdom}.${URL_TEMPLATE}" \
        scanapi run \
        -o "/shared/results/${HOSTNAME}-${sdom}-report.csv" \
        -t "/shared/shared_data/csv_template.jinja" \
        /shared/shared_data/scanapi.yaml
done
