import argparse
import socket
import sys
import uuid
import redis
import time

from redis.backoff import ExponentialBackoff
from redis.exceptions import RedisError, TimeoutError, ConnectionError, AuthenticationError
from redis.retry import Retry

from iam_authtoken_request import ElastiCacheIAMProvider

# Specify the input parameter options
def parse_arguments():
    parser = argparse.ArgumentParser(description='Connect to a cluster using the demo app')

    parser.add_argument("--user-id", dest="user_id", required=True)
    parser.add_argument("--replication-group-id", dest="replication_group_id", required=True, help="Elasticache/MemoryDB for Redis/Valkey Cluster name")
    parser.add_argument("--region", required=True)
    parser.add_argument("--redis-host", dest="redis_host", required=True, help="Cluster endpoint")
    parser.add_argument("--redis-port", dest="redis_port", type=int, default=6379)
    parser.add_argument("--tls", action="store_true", default=False, help="TLS enabled")
    parser.add_argument("--cluster-mode", dest="cluster_mode", action="store_true", default=False, help="Cluster mode enabled")
    parser.add_argument("--connect-sleep-time", dest="connect_sleep_time", type=int, default=1)
    parser.add_argument("--memorydb-service", dest="is_memorydb", action="store_true", default=False, help="For MemoryDB IAM authentication")

    parser.add_argument("--debug", action="store_true", default=False, help="Print the caller identity")

    return parser.parse_args()

# Generate random key name
def get_rand_key():
    return str(uuid.uuid4())

# Demo App for ElastiCache/MemoryDB for Redis/Valkey IAM Authentication
def main():
    try:
        args = parse_arguments()
        creds_provider = ElastiCacheIAMProvider(user=args.user_id, cluster_name=args.replication_group_id,
                                                region=args.region, debug=args.debug, is_memorydb=args.is_memorydb)

        if not args.debug:
            print(f"Using credentials: {str(creds_provider.get_credentials())}")

        # Construct Redis connection with credentials provider
        retry = Retry(
            backoff=ExponentialBackoff(cap=10, base=1),
            retries=3,
            supported_errors=(
                ConnectionError,
                TimeoutError,
                socket.timeout
            )
        )

        cluster_mode = args.cluster_mode
        # cluster_mode = True if args.is_memorydb else args.cluster_mode
        if not cluster_mode:
            user_connection = redis.Redis(host=args.redis_host, port=args.redis_port, ssl=args.tls,
                                          credential_provider=creds_provider,
                                          health_check_interval=600,  # ping every 10 min
                                          retry=retry,
                                          retry_on_error=[RedisError, TimeoutError, ConnectionResetError, AuthenticationError])
        else:
            user_connection = redis.RedisCluster(host=args.redis_host, port=args.redis_port, ssl=args.tls,
                                                 credential_provider=creds_provider,
                                                 health_check_interval=600,  # ping every 10 min
                                                 retry=retry,
                                                 retry_on_error=[RedisError, TimeoutError, ConnectionResetError, AuthenticationError])

        num_requests = 0
        num_failed = 0
        while True:
            # print(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
            try:
                user_connection.get(get_rand_key())
                num_requests += 1
                num_failed = 0
                print(f"=> Successful requests: {str(num_requests)}")
            except Exception as e:
                print(f"Error: {str(e)}")
                num_failed += 1
                if num_failed >= 10:
                    break

            time.sleep(args.connect_sleep_time)

        return 0
    except KeyboardInterrupt:
        # Press Ctrl^c to exit
        print("Program execution was interrupted and exited")
        return 0
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

