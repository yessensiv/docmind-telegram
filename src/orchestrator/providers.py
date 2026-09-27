"""Provider boundary. Network execution is deliberately disabled."""


class ApiDisabledError(RuntimeError):
    """Raised if code attempts to perform a model API call."""


def generate(*args, **kwargs):
    raise ApiDisabledError("API calls are disabled in the offline orchestrator")
