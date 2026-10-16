"""Local spaces shim for HF Spaces ZeroGPU startup scan.

Provides a no-op @spaces.GPU decorator so HF Spaces detects a GPU function
without pulling in the real spaces package (which drags gradio 6.x and
conflicts with aiogram's pydantic requirement).
"""

import functools


def GPU(fn=None, *, gpu_image=None):
    """No-op GPU decorator. Satisfies HF Spaces startup scan."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    if fn is None:
        return decorator
    return decorator(fn)


__all__ = ["GPU"]
