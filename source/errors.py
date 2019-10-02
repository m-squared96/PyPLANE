class PPException(Exception):
    """
    Base exception class for PyPLANE
    """

    def __init__(self, message, *args, **kwargs):
        self.message = message
        self.args = args
        self.kwargs = kwargs


class ParameterTypeError(PPException):
    """
    ParameterTypeError: Inherits from PPException

    To be used when parameters passed to SOE are not of numerical type
    """

    def __init__(self, message, *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class ParameterValidityError(PPException):
    """
    ParameterValidityError: Inherits from PPException

    To be used when parameter key:value pairs are invalid due to:
        1. Missing/undefined keys
        2. Non-compliant keys
    """

    def __init__(self, message, *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class LimitTypeError(PPException):
    """
    LimitTypeError: Inherits from PPException

    To be used when axes limits passed to SOE are not of numerical type
    """

    def __init__(self, message, *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class LimitMagnitudeError(PPException):
    """
    LimitMagnitudeError: Inherits from PPException

    To be used when the max limit of an axis is less than or equal to
    the min limit of that same axis
    """

    def __init__(self, message, *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class MathematicalOperationError(PPException):
    """
    MathematicalOperationError: Inherits from PPException

    To be used when an invalid mathematical operation is being
    invoked in the ODE expressions being passed to SOE.

    For example, division by zero
    """

    def __init__(self, message, *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class MathematicalFunctionError(PPException):
    """
    MathematicalFunctionError: Inherits from PPException

    To be used when an unrecognised mathematical function is
    being invoked in the ODE expressions being passed to SOE.

    For example, arcsin vs asin, etc.
    """

    def __init__(self, message, *args, **kwargs):
        super().__init__(message, *args, **kwargs)
