#!/bin/sh

CLIENT_IPS="2001:db8:1::10 192.168.0.40 2001:db8:1::60 2001:db8:1::664"

sleep 30
for client in ${CLIENT_IPS}; do
    while ping -c 1 -W 1 "${client}" >/dev/null 2>&1; do sleep 1; done
    echo "Client IP ${client} is now offline"
done

echo "All clients are now offline. Shutting down"