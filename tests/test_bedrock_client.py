import json

import pytest
from botocore.exceptions import ClientError

from aws_ai.bedrock_client import BedrockIPv6Client, BedrockInvocationError


def valid_report_json():
    return json.dumps(
        {
            "overall_readiness": "READY",
            "overall_score": 90,
            "executive_summary": "Assessment interpreted from deterministic data.",
            "critical_issues": [],
            "device_assessments": [],
            "configuration_recommendations": [],
            "routing_recommendations": [],
            "transition_recommendations": [],
            "device_replacements": [],
            "migration_priorities": [],
            "risks": [],
            "next_steps": [],
        }
    )


class FakeRuntimeClient:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.requests = []

    def converse(self, **kwargs):
        self.requests.append(kwargs)
        response = next(self.responses)
        if isinstance(response, Exception):
            raise response
        return response


def success_response(text=None):
    return {"output": {"message": {"content": [{"text": text or valid_report_json()}]}}}


def test_bedrock_request_and_response_are_validated():
    runtime = FakeRuntimeClient([success_response()])
    client = BedrockIPv6Client(
        model_id="example.model",
        region_name="us-east-1",
        runtime_client=runtime,
        sleep_fn=lambda _: None,
    )

    report = client.assess({"network_name": "Lab", "devices": []})

    assert report.overall_readiness == "READY"
    request = runtime.requests[0]
    assert request["modelId"] == "example.model"
    assert "Lab" in request["messages"][0]["content"][0]["text"]
    assert "IPv6 network migration" in request["system"][0]["text"]


def test_bedrock_extracts_fenced_json_and_rejects_invalid_report():
    runtime = FakeRuntimeClient([success_response("```json\n" + valid_report_json() + "\n```")])
    client = BedrockIPv6Client("model", "us-east-1", runtime, sleep_fn=lambda _: None)
    assert client.assess({}).overall_score == 90.0

    invalid_runtime = FakeRuntimeClient([success_response("not-json")])
    invalid_client = BedrockIPv6Client("model", "us-east-1", invalid_runtime)
    with pytest.raises(BedrockInvocationError):
        invalid_client.assess({})


def test_bedrock_retries_transient_error_and_handles_nontransient_error():
    throttled = ClientError(
        {"Error": {"Code": "ThrottlingException"}, "ResponseMetadata": {"HTTPStatusCode": 429}},
        "Converse",
    )
    runtime = FakeRuntimeClient([throttled, success_response()])
    client = BedrockIPv6Client("model", "us-east-1", runtime, sleep_fn=lambda _: None)
    assert client.assess({}).overall_readiness == "READY"
    assert len(runtime.requests) == 2

    denied = ClientError(
        {"Error": {"Code": "AccessDeniedException"}, "ResponseMetadata": {"HTTPStatusCode": 403}},
        "Converse",
    )
    denied_client = BedrockIPv6Client(
        "model", "us-east-1", FakeRuntimeClient([denied]), sleep_fn=lambda _: None
    )
    with pytest.raises(BedrockInvocationError):
        denied_client.assess({})
