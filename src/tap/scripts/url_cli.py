from __future__ import annotations

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Extract text content from a URL via Siphon."
    )
    parser.add_argument("url", help="URL to extract content from.")
    args = parser.parse_args()

    from siphon_api.api.siphon_request import SiphonRequestParams
    from siphon_api.api.to_siphon_request import create_siphon_request
    from siphon_api.enums import ActionType
    from siphon_api.models import ContentData
    from headwater_client.client.headwater_client import HeadwaterClient

    params = SiphonRequestParams(action=ActionType.EXTRACT)
    request = create_siphon_request(source=args.url, request_params=params)
    client = HeadwaterClient()
    response = client.siphon.process(request)
    payload = response.payload
    if not isinstance(payload, ContentData):
        print(f"Error: unexpected response type {type(payload)}", file=sys.stderr)
        sys.exit(1)
    print(payload.text)


if __name__ == "__main__":
    main()
