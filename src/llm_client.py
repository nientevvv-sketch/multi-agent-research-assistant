
from openai import (
    OpenAI,
    AuthenticationError,
    RateLimitError,
    APIConnectionError,
    APIStatusError,
)

from src.config import OPENAI_API_KEY, OPENAI_MODEL


client = OpenAI(api_key=OPENAI_API_KEY)


def get_error_code(error) -> str:
    """Extract the API error code."""

    code = getattr(error, "code", None)

    if code:
        return str(code)

    body = getattr(error, "body", None)

    if isinstance(body, dict):
        error_data = body.get("error", body)

        if isinstance(error_data, dict):
            code = error_data.get("code")

            if code:
                return str(code)

    return "unknown"


def generate_response(prompt: str) -> str:
    """Generate a response using the OpenAI API."""

    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    try:
        response = client.responses.create(
            model=OPENAI_MODEL,
            input=prompt,
            max_output_tokens=1200
        )

    except AuthenticationError as error:
        raise RuntimeError(
            "OpenAI authentication failed. Check your API key."
        ) from error

    except RateLimitError as error:
        error_code = get_error_code(error)

        print("\n--- OPENAI RATE LIMIT DIAGNOSTICS ---")
        print("Error code:", error_code)
        print("Error message:", str(error))

        response = getattr(error, "response", None)

        if response is not None:
            for name, value in response.headers.items():
                if (
                    "ratelimit" in name.lower()
                    or "retry-after" in name.lower()
                ):
                    print(f"{name}: {value}")

        print("--- END DIAGNOSTICS ---\n")

        raise RuntimeError(
            "OpenAI rate limit exceeded. "
            f"Error code: {error_code}."
        ) from error

    except APIConnectionError as error:
        raise RuntimeError(
            "Could not connect to the OpenAI API. "
            "Check your internet connection."
        ) from error

    except APIStatusError as error:
        raise RuntimeError(
            f"OpenAI API returned an error (HTTP {error.status_code})."
        ) from error

    result = response.output_text

    if not isinstance(result, str) or not result.strip():
        raise RuntimeError("OpenAI returned an empty response.")

    return result
