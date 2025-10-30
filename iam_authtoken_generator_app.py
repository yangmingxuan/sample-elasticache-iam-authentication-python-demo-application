import argparse
import sys

from iam_authtoken_request import ElastiCacheIAMProvider

# Specify the input parameter options
def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate a token using the demo app')

    parser.add_argument("--user-id", dest="user_id", required=True)
    parser.add_argument("--replication-group-id", dest="replication_group_id", required=True)
    parser.add_argument("--region", required=True)
    parser.add_argument("--memorydb-service", dest="is_memorydb", action="store_true", default=False, help="For MemoryDB IAM authentication")

    parser.add_argument("--debug", action="store_true", default=False, help="Print the caller identity")

    return parser.parse_args()


# Generate an IAM Auth token
def main():
    try:
        args = parse_arguments()

        creds_provider = ElastiCacheIAMProvider(user=args.user_id, cluster_name=args.replication_group_id,
                                                region=args.region, debug=args.debug, is_memorydb=args.is_memorydb)
        print(creds_provider.get_credentials()[1])

        return 0
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
