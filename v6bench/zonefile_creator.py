from pathlib import Path
import ipaddress
import argparse
import datetime
import socket


DEFAULT_NS   = ["192.168.0.53", "2001:db8::53"]  # noqa: E221
DEFAULT_SIIT = ["192.168.46.1"]


def ip2dnsrec(ip, host):
    match ipaddress.ip_address(ip).version:
        case 4:
            return f"{host}\tIN\tA\t{ip}"
        case 6:
            return f"{host}\tIN\tAAAA\t{ip}"


def parseargs():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "domain",
        help="Domain of the service to be tested",
    )

    parser.add_argument(
        "--ns-ips",
        nargs="+",
        default=DEFAULT_NS,
        metavar="NS",
        help="List of Name Server IPs containing at least one IPv4 and one IPv6 address",  # noqa:E501
    )

    parser.add_argument(
        "--siit-ips",
        nargs="+",
        default=DEFAULT_SIIT,
        metavar="SIIT",
        help="List of SIIT IPv4 addresses",
    )

    args = parser.parse_args()

    # Validate NS-IPs list
    has_v4 = any(ipaddress.ip_address(a).version == 4 for a in args.ns_ips)
    has_v6 = any(ipaddress.ip_address(a).version == 6 for a in args.ns_ips)

    if not has_v4 or not has_v6:
        parser.error("--ns-ips must contain at least one IPv4 and one IPv6 address")  # noqa:

    # Validate SIIT-IPs list
    if any(ipaddress.ip_address(a).version != 4 for a in args.siit_ips):
        parser.error("--siit-ips must contain exclusivelly IPv4 addresses")

    return args


def dom2ips(domain):
    ips = socket.getaddrinfo(domain, None, family=socket.AF_UNSPEC)

    ip_dict = {socket.AF_INET: set(), socket.AF_INET6: set()}
    for entry in ips:
        family = entry[0]
        ip = entry[-1][0]
        ip_dict[family].add(ip)
    return ip_dict


def build_zf_string(args):
    serial = datetime.datetime.now(datetime.UTC).strftime("%Y%m%d01")
    siit_recs = [ip2dnsrec(a, 'siit') for a in args.siit_ips]
    ns_recs = [ip2dnsrec(a, 'ns') for a in args.ns_ips]

    lines = [
        "$TTL 3600",
        f"@\tIN\tSOA\tns.lab.{args.domain}.\thostmaster.lab.{args.domain}. (",
        f"\t{serial}",
        "\t3600",
        "\t900",
        "\t1209600",
        "\t300",
        ")",
        "",
        "@\tIN\tNS\tns.lab.",
    ]
    lines.extend(ns_recs)
    lines.append("")
    lines.extend(siit_recs)

    ip_dict = dom2ips(args.domain)

    zone_dict = {
        "dual": list(ip_dict[socket.AF_INET6].union(ip_dict[socket.AF_INET])),
        "ipv4": list(ip_dict[socket.AF_INET]),
        "ipv6": list(ip_dict[socket.AF_INET6])
    }

    for host, addrs in zone_dict.items():
        for addr in addrs:
            lines.append(ip2dnsrec(addr, host))
    lines.append("")

    return "\n".join(lines)


def main():

    SCRIPT_PATH = Path(__file__).resolve().parent
    BIND_PATH = f"{SCRIPT_PATH}/kathara/dns/etc/bindfiles"

    args = parseargs()

    zf_string = build_zf_string(args)

    with open(f"{BIND_PATH}/db.lab", "w") as f:
        f.write(zf_string)

    with open(f"{BIND_PATH}/named.conf.lab-zones", "w") as f:
        f.write(f"""zone "lab.{args.domain}" {{
        type master;
        file "/etc/bind/db.lab"; # Path to the zone file
    }};
""")


if __name__ == '__main__':
    main()
