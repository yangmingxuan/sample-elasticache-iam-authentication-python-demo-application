from typing import Tuple, Union
from urllib.parse import ParseResult, urlencode, urlunparse

import botocore.session
import redis
from botocore.model import ServiceId
from botocore.signers import RequestSigner
from cachetools import TTLCache, cached

class ElastiCacheIAMProvider(redis.CredentialProvider):
    def __init__(self, user, cluster_name, region, debug=False, is_memorydb=False):
        self.user = user
        self.cluster_name = cluster_name
        self.region = region
        self.debug = debug

        session = botocore.session.get_session()
        self.request_signer = RequestSigner(
            ServiceId("memorydb" if is_memorydb else "elasticache"),
            self.region,
            "memorydb" if is_memorydb else "elasticache",
            "v4",
            session.get_credentials(),
            session.get_component("event_emitter"),
        )

        # Display the actual caller identity being used by the program
        if self.debug:
            try:
                caller_identity = session.create_client('sts').get_caller_identity()
                print(f"Current Role/User ARN: {caller_identity['Arn']}")
            except Exception as e:
                print(f"Error in getting caller identity: {str(e)}")

    # Generated IAM tokens are valid for 15 minutes
    @cached(cache=TTLCache(maxsize=1, ttl=900))
    def get_credentials(self) -> Union[Tuple[str], Tuple[str, str]]:
        query_params = {"Action": "connect", "User": self.user}
        url = urlunparse(
            ParseResult(
                scheme="https",
                netloc=self.cluster_name,
                path="/",
                query=urlencode(query_params),
                params="",
                fragment="",
            )
        )
        signed_url = self.request_signer.generate_presigned_url(
            {"method": "GET", "url": url, "body": {}, "headers": {}, "context": {}},
            operation_name="connect",
            expires_in=900,
            region_name=self.region,
        )
        # RequestSigner only seems to work if the URL has a protocol, but
        # Elasticache only accepts the URL without a protocol
        # So strip it off the signed URL before returning
        if self.debug:
            print(f"Using credentials: {self.user} {signed_url.removeprefix('https://')}")
        return self.user, signed_url.removeprefix("https://")

