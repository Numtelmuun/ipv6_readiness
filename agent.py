import asyncio

from mcp_client import call_tool


async def assess_network():

    result = await call_tool(
        "assess_all_ipv6_devices",
        {}
    )

    return result


def generate_report(data):

    summary = data["summary"]

    total = summary["total_devices"]
    ready = summary["ready"]
    mostly_ready = summary["mostly_ready"]
    partially_ready = summary["partially_ready"]
    not_ready = summary["not_ready"]

    average = data["average_score"]

    print("\n")
    print("=" * 60)
    print("AI IPv6 READINESS REPORT")
    print("=" * 60)

    print(f"\nTotal devices: {total}")
    print(f"Average score: {average}%")

    print("\nReadiness:")
    print(f"  READY:           {ready}")
    print(f"  MOSTLY_READY:    {mostly_ready}")
    print(f"  PARTIALLY_READY: {partially_ready}")
    print(f"  NOT_READY:       {not_ready}")

    print("\nDevices:")

    for device in data["devices"]:

        print(
            f"  {device['device']:5} "
            f"{device['role']:5} "
            f"{device['score']:5}% "
            f"{device['readiness']}"
        )

    recommendations = data.get(
        "recommendations",
        []
    )

    print("\nRecommendations:")

    if not recommendations:

        print("  No recommendations.")

    else:

        for recommendation in recommendations:

            print(
                f"  [{recommendation['severity']}] "
                f"{recommendation['device']} - "
                f"{recommendation['id']}"
            )

            print(
                f"      {recommendation['recommendation']}"
            )


async def main():

    data = await assess_network()

    generate_report(data)


if __name__ == "__main__":

    asyncio.run(main())