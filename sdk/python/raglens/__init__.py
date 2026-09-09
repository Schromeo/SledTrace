import warnings

from .trace import trace, RAGLensTrace, SledTraceTrace
from .chunks import ChunkNormalizationError, normalize_chunk, normalize_chunks

__version__ = "0.7.0"

warnings.warn(
    "The 'raglens' package is deprecated and kept only for temporary compatibility. "
    "Please import from 'sledtrace' instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "__version__",
    "trace",
    "SledTraceTrace",
    "RAGLensTrace",
    "ChunkNormalizationError",
    "normalize_chunk",
    "normalize_chunks",
]
