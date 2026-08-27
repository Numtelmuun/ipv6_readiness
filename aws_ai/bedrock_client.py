"""Amazon Bedrock Runtime adapter used by the local IPv6 assessment app."""

from __future__ import annotations

import json
import os
import time
from typing import Any, Callable

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from models.ai_report import AIReport, AIReportValidationError


SYSTEM_INSTRUCTION = """You are an IPv6 network migration and readiness expert.
Analyze only the provided deterministic assessment JSON. The normalized device
data is collected evidence and the deterministic assessment is the factual
source of truth. Do not invent device capabilities, configurations, topology,
or migration facts. When a value is unknown or absent, explicitly describe it
as unknown. Clearly distinguish collected facts, deterministic findings, and
your recommendations.

Return JSON only, with exactly these fields:
executive_summary, critical_issues, device_assessments,
configuration_recommendations, routing_recommendations,
transition_recommendations, device_replacements, migration_priorities, risks,
next_steps.

Every listed field except executive_summary must be an array of JSON objects.
Each device_assessments entry must contain only the exact device or hostname
identifier from the input plus interpretive content. Do not echo or generate
vendor, model, platform, device_type, role, score, or readiness; local report
composition supplies those deterministic fields. Omit a device rather than
inventing an identifier. Each recommendation must state its basis, use
recommendation_type best_practice or detected_deficiency, and include finding_ids
for a detected deficiency. Empty arrays are valid when the input does not
support a conclusion."""


class BedrockConfigurationError(ValueError):
    """Raised when local Bedrock configuration is incomplete."""


class BedrockInvocationError(RuntimeError):
    """Raised when Bedrock cannot provide a valid response."""


TRANSIENT_ERROR_CODES = {
    "InternalServerException",
    "ModelTimeoutException",
    "ServiceUnavailableException",
    "ThrottlingException",
    "TooManyRequestsException",
}
TRANSIENT_HTTP_STATUSES = {429, 500, 502, 503, 504}


class BedrockIPv6Client:
    """Call Bedrock Converse through boto3's normal credential chain."""

    def __init__(
        self,
        model_id: str | None = None,
        region_name: str | None = None,
        runtime_client: Any | None = None,
        max_attempts: int = 3,
        sleep_fn: Callable[[float], None] = time.sleep,
    ):
        self.model_id = model_id or os.getenv("AWS_BEDROCK_MODEL_ID")
        self.region_name = (
            region_name
            or os.getenv("AWS_REGION")
            or os.getenv("AWS_DEFAULT_REGION")
        )

        if not self.model_id:
            raise BedrockConfigurationError(
                "AWS_BEDROCK_MODEL_ID must be configured."
            )
        if not self.region_name:
            raise BedrockConfigurationError(
                "AWS_REGION must be configured."
            )
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1.")

        self.max_attempts = max_attempts
        self.sleep_fn = sleep_fn
        self.runtime_client = runtime_client or boto3.client(
            "bedrock-runtime",
            region_name=self.region_name,
        )

    def build_request(self, assessment_payload: dict) -> dict[str, Any]:
        """Build the provider-neutral Bedrock Converse request."""

        payload_json = json.dumps(
            assessment_payload,
            ensure_ascii=False,
            sort_keys=True,
        )
        return {
            "modelId": self.model_id,
            "system": [{"text": SYSTEM_INSTRUCTION}],
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": (
                                "Analyze this completed local IPv6 readiness "
                                "assessment and return the required JSON only:\n"
                                + payload_json
                            )
                        }
                    ],
                }
            ],
            "inferenceConfig": {
                "maxTokens": 4096,
                "temperature": 0.1,
            },
        }

    def assess(self, assessment_payload: dict) -> AIReport:
        request = self.build_request(assessment_payload)
        response = self._converse_with_retry(request)
        output = self.extract_text(response)

        try:
            return AIReport.from_json(self._strip_json_fence(output))
        except AIReportValidationError as error:
            raise BedrockInvocationError(
                "Bedrock returned an invalid IPv6 AI report."
            ) from error

    def _converse_with_retry(self, request: dict[str, Any]) -> dict[str, Any]:
        for attempt in range(1, self.max_attempts + 1):
            try:
                return self.runtime_client.converse(**request)
            except ClientError as error:
                if not self._is_transient_client_error(error):
                    raise BedrockInvocationError(
                        "Bedrock rejected the inference request."
                    ) from error
                if attempt == self.max_attempts:
                    raise BedrockInvocationError(
                        "Bedrock inference failed after transient retries."
                    ) from error
            except BotoCoreError as error:
                if attempt == self.max_attempts:
                    raise BedrockInvocationError(
                        "Bedrock connection failed after transient retries."
                    ) from error

            self.sleep_fn(0.5 * (2 ** (attempt - 1)))

        raise BedrockInvocationError("Bedrock inference did not return a response.")

    @staticmethod
    def _is_transient_client_error(error: ClientError) -> bool:
        details = error.response.get("Error", {})
        metadata = error.response.get("ResponseMetadata", {})
        return (
            details.get("Code") in TRANSIENT_ERROR_CODES
            or metadata.get("HTTPStatusCode") in TRANSIENT_HTTP_STATUSES
        )

    @staticmethod
    def extract_text(response: dict[str, Any]) -> str:
        try:
            content = response["output"]["message"]["content"]
            text = "".join(
                item["text"]
                for item in content
                if isinstance(item, dict) and isinstance(item.get("text"), str)
            )
        except (KeyError, TypeError) as error:
            raise BedrockInvocationError(
                "Bedrock response did not contain message text."
            ) from error

        if not text.strip():
            raise BedrockInvocationError("Bedrock response contained no message text.")
        return text

    @staticmethod
    def _strip_json_fence(value: str) -> str:
        value = value.strip()
        if value.startswith("```") and value.endswith("```"):
            value = value.split("\n", 1)[1] if "\n" in value else ""
            value = value.rsplit("```", 1)[0]
        return value.strip()
