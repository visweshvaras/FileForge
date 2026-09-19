"""
Auto-discovery Plugin Registry for FileForge / OpenForge.

Scans the plugins/ directory for community tools, dynamically registers them,
and exposes them to the main terminal menu without requiring changes to core code.
"""
import os
import sys
import importlib
import inspect
from typing import Dict, List, Tuple, Type
from plugins.base_tool import BaseTool

class PluginRegistry:
    def __init__(self, plugins_dir: str = None):
        if plugins_dir is None:
            plugins_dir = os.path.dirname(os.path.abspath(__file__))
        self.plugins_dir = plugins_dir
        self.plugins: Dict[str, BaseTool] = {}
        self.number_map: Dict[str, BaseTool] = {}
        self._load_plugins()

    def _load_plugins(self):
        """Scans plugins directory and imports all subclasses of BaseTool."""
        self.plugins.clear()

        # Ensure parent directory is in sys.path
        parent_dir = os.path.dirname(self.plugins_dir)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)

        # Ignore internal files
        ignored_files = {"__init__.py", "base_tool.py", "registry.py"}

        for item in sorted(os.listdir(self.plugins_dir)):
            if item.startswith("_") or item.startswith("."):
                continue

            module_name = None
            item_path = os.path.join(self.plugins_dir, item)

            if os.path.isfile(item_path) and item.endswith(".py"):
                if item in ignored_files:
                    continue
                module_name = f"plugins.{item[:-3]}"
            elif os.path.isdir(item_path) and os.path.isfile(os.path.join(item_path, "__init__.py")):
                module_name = f"plugins.{item}"

            if module_name:
                try:
                    mod = importlib.import_module(module_name)
                    # Find all classes that inherit from BaseTool (excluding BaseTool itself)
                    for _, cls in inspect.getmembers(mod, inspect.isclass):
                        if issubclass(cls, BaseTool) and cls is not BaseTool:
                            instance = cls()
                            self.plugins[instance.id] = instance
                except Exception as e:
                    # Print warning if a plugin fails to import, without crashing the main application
                    print(f"⚠️  [Plugin Warning] Could not load plugin '{module_name}': {e}")

    def get_all(self) -> List[BaseTool]:
        """Return list of all registered plugin instances."""
        return list(self.plugins.values())

    def get_by_id(self, tool_id: str) -> BaseTool:
        return self.plugins.get(tool_id)

    def get_by_number(self, number_str: str) -> BaseTool:
        return self.number_map.get(str(number_str))

    def build_menu_categories(self, start_number: int = 17) -> List[Tuple[str, List[Tuple[str, str, str]]]]:
        """
        Organizes all discovered plugins into menu categories and assigns option numbers.
        Returns a list of (Category_Name, [(Option_Number, Title, Description), ...])
        """
        self.number_map.clear()
        if not self.plugins:
            return []

        categories: Dict[str, List[Tuple[str, str, str]]] = {}
        curr_num = start_number

        for plugin in self.plugins.values():
            cat = plugin.category or "✨ COMMUNITY EXTENSIONS"
            if cat not in categories:
                categories[cat] = []

            num_str = str(curr_num)
            title = f"{plugin.icon}  {plugin.name}"
            desc = f"{plugin.description} {f'({plugin.author})' if plugin.author else ''}"
            categories[cat].append((num_str, title, desc))
            self.number_map[num_str] = plugin
            curr_num += 1

        return list(categories.items())

# Global singleton registry
registry = PluginRegistry()
