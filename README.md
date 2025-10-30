# Elasticache IAM authentication Python demo application

You can use this python-based application which uses the Redis-py client to demo the IAM based Authentication to access your Elasticache/MemoryDB for Redis/Valkey cluster.

NOTE: Make sure that The EC2 instance is in the same VPC as the ElastiCache cluster. Also this application works only with Elasticache/MemoryDB for Redis/Valkey version 7.0 or higher with TLS enabled.

## Getting started with setting up the EC2 instance to run the Demo application.

### Prerequisites
According to documentation [Authenticating with IAM for Elasticache](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/auth-iam.html) or [Authenticating with IAM for MemoryDB](https://docs.aws.amazon.com/memorydb/latest/devguide/auth-iam.html) , set up IAM user/role permission policies, create Elasticache/MemoryDB users(type=iam) for Redis/Valkey clusters, generate access strings, and complete other required steps.

The app uses the [botocore session get credentials](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/core/session.html#boto3.session.Session.get_credentials) to generate the IAM Auth token (signs the token) using your current AWS caller identity. If you setup your IAM role as EC2 instance profile, then the temporary credentials for the IAM role will be automatically managed for you.

### Install required Python3 modules

Please use Python 3.10 or higher. Use the following command to check your Python3 version:
```
python3 --version
```
Please install the following Python3 modules:
```
pip3 install boto3

pip3 install redis

pip3 install cachetools
```

## Usage Instructions

This software package contains a token generation program and connection example code. You can use the -h parameter to view required and optional parameters:

```python3 ./iam_authtoken_generator_app.py -h```
```
usage: iam_authtoken_generator_app.py [-h] --user-id USER_ID --replication-group-id REPLICATION_GROUP_ID --region REGION [--memorydb-service] [--debug]

Generate a token using the demo app

options:
  -h, --help            show this help message and exit
  --user-id USER_ID
  --replication-group-id REPLICATION_GROUP_ID
  --region REGION
  --memorydb-service    For MemoryDB IAM authentication
  --debug               Print the caller identity
```

```python3 ./iam_auth_demo_app.py -h```
```
usage: iam_auth_demo_app.py [-h] --user-id USER_ID --replication-group-id REPLICATION_GROUP_ID --region REGION --redis-host REDIS_HOST
                            [--redis-port REDIS_PORT] [--tls] [--cluster-mode] [--connect-sleep-time CONNECT_SLEEP_TIME] [--memorydb-service] [--debug]

Connect to a cluster using the demo app

options:
  -h, --help            show this help message and exit
  --user-id USER_ID
  --replication-group-id REPLICATION_GROUP_ID
                        Elasticache/MemoryDB for Redis/Valkey Cluster name
  --region REGION
  --redis-host REDIS_HOST
                        Cluster endpoint
  --redis-port REDIS_PORT
  --tls                 TLS enabled
  --cluster-mode        Cluster mode enabled
  --connect-sleep-time CONNECT_SLEEP_TIME
  --memorydb-service    For MemoryDB IAM authentication
  --debug               Print the caller identity

```

### To generate a token using the demo app use the following command
```
python3 ./iam_authtoken_generator_app.py --replication-group-id <iamtestcluster> --user-id <iamuser> --region <us-west-2>
```
#### To generate MemoryDB token
```
python3 ./iam_authtoken_generator_app.py --replication-group-id <iamtestcluster> --user-id <iamuser> --region <us-west-2> --memorydb-service
```

### To connect to a cluster using the demo app

```
python3 ./iam_auth_demo_app.py --user-id <iamuser> --replication-group-id <iamtestcluster> --region <us-west-2> --redis-host <endpoint> --tls [--cluster-mode] --connect-sleep-time 10
```
#### To connect to a MemoryDB cluster
```
python3 ./iam_auth_demo_app.py --user-id <iamuser> --replication-group-id <testmemorydb> --region <us-west-2> --redis-host <endpoint> --tls --cluster-mode --connect-sleep-time 10 --memorydb-service
```


For cluster-mode enabled replication groups, please add the `--cluster-mode` flag.

The demo app creates a new connection to the host using the IAM user identity and generates an IAM authentication token.

## Auto Reconnect
An IAM authenticated connection to ElastiCache for Valkey or Redis OSS will automatically be disconnected after 12 hours. This program automatically reconnects using a new IAM authentication token after the server disconnects.


