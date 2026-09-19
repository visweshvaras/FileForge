"""
Base Converter Engine Interface
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseEngine(ABC):
    """Abstract base class for PPT to PDF conversion engines."""

    name: str = "base"
    description: str = "Base engine"

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if this engine is available on the current system."""
        pass

    @abstractmethod
    def convert(
        self,
        input_path: str,
        output_path: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Convert presentation file to PDF.

        Args:
            input_path: Path to .pptx or .ppt file.
            output_path: Path to destination .pdf file.
            **kwargs: Engine-specific options.

        Returns:
            dict containing conversion results:
                success: bool
                engine: str
                output_path: str
                slide_count: int
                duration_seconds: float
                file_size_bytes: int
                error: Optional[str]
        """
        pass
