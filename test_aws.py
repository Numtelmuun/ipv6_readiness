import boto3


def main():

    sts = boto3.client("sts")

    identity = sts.get_caller_identity()

    print("=" * 60)
    print("AWS CONNECTION TEST")
    print("=" * 60)

    print("Account:", identity["Account"])
    print("ARN:", identity["Arn"])


if __name__ == "__main__":
    main()