"""
Base class definition for all OpenForge / FileForge modular plugins and tools.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

class BaseTool(ABC):
    """
    Every new tool or converter created by the community inherits from BaseTool.
    
    This ensures that new tools can be added to FileForge simply by dropping
    a Python file or folder into the `plugins/` directory, without modifying
    main.py or terminal_menu.py (preventing Git merge conflicts).
    """
    
    # Required metadata
    id: str = "custom_tool"
    name: str = "My Custom Tool"
    description: str = "A community-contributed utility tool"
    category: str = "✨ COMMUNITY PLUGINS"
    icon: str = "⚡"
    author: str = "@OpenForge"
    version: str = "1.0.0"
    
    # Optional list of required pip packages (e.g. ['tesseract', 'markdown'])
    dependencies: List[str] = []

    def check_dependencies(self) -> bool:
        """Check if all required python packages are installed."""
        missing = []
        for dep in self.dependencies:
            try:
                __import__(dep)
            except ImportError:
                missing.append(dep)
        
        if missing:
            print(f"\n⚠️  [DEPENDENCY NOTICE] '{self.name}' requires additional packages:")
            print(f"   Run: pip install {' '.join(missing)}\n")
            return False
        return True

    @abstractmethod
    def run(self) -> None:
        """
        Main execution logic for the tool.
        This is called when the user selects this tool from the menu.
        """
        pass
