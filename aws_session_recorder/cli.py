"""Console script for aws_session_recorder."""
import argparse
import sys
from aws_session_recorder import lib
import IPython  # type: ignore
from mypy_boto3_iam import client  # type: ignore

def main():
    """Console script for aws_session_recorder."""
    parser = argparse.ArgumentParser()
    parser.add_argument('shell', type=bool)
    parser.add_argument('--profile-name', type=str, default='')
    args = parser.parse_args()

    if args.profile_name:
        sess = lib.Session(profile_name=args.profile_name)
    else:
        sess = lib.Session()

    if args.shell:
        from aws_session_recorder.lib import schema
        iam: client.IAMClient = sess.client('iam')
        IPython.embed()
    else:
        print(parser.format_help())
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
