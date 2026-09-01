import sys
import yaml


HOST_HEADER = "${BASE_DOMAIN}"


def add_host_headers(data):
    """Add Host header to every request in the ScanAPI document."""

    for endpoint in data.get("endpoints", []):
        for request in endpoint.get("requests", []):
            headers = request.setdefault("headers", {})

            # Don't overwrite an existing Host header
            if "Host" not in headers:
                headers["Host"] = HOST_HEADER


def main():
    filename = "scanapi.yaml"

    if len(sys.argv) > 1:
        filename = sys.argv[1]

    with open(filename, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError("Invalid scanapi.yaml: expected a YAML mapping at the root.")  # noqa: E501

    add_host_headers(data)

    with open(filename, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            data,
            f,
            sort_keys=False,
            default_flow_style=False,
            allow_unicode=True,
        )

    print(f"Updated {filename}")


if __name__ == "__main__":
    main()
