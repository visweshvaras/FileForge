#!/usr/bin/env python3
"""
OpenForge Community Tool Scaffolder / Generator.

Helps students and contributors easily create a brand-new pluggable tool
with boilerplate code, GUI file pickers, and auto-registration.
"""
import os
import sys
import re

def slugify(text: str) -> str:
    """Convert a human-readable title into a python module name."""
    s = re.sub(r'[^a-zA-Z0-9\s_]', '', text.lower())
    return re.sub(r'\s+', '_', s.strip())

TEMPLATE = '''"""
Community Plugin: {name}
Author: {author}
"""
import os
from plugins.base_tool import BaseTool
from ui.dialogs import choose_input_files, choose_save_location
from ui.terminal_menu import print_success_card, print_error_card, CYAN, BOLD, RESET
from utils.helper import open_file_or_dir

class {class_name}(BaseTool):
    id = "{tool_id}"
    name = "{name}"
    description = "{description}"
    category = "{category}"
    icon = "{icon}"
    author = "{author}"
    version = "1.0.0"
    dependencies = {dependencies}

    def run(self) -> None:
        """Main tool logic executed when selected from the menu."""
        if not self.check_dependencies():
            return

        print(f"\\n{{CYAN}}{{BOLD}}▶ {{self.icon}} Starting {{self.name}}...{{RESET}}")

        # 1. Ask user to pick input file(s)
        files = choose_input_files(
            title="Select Input File",
            file_filters=["*.*"],
            multiple=False
        )
        if not files:
            print("Operation cancelled. No file selected.")
            return

        input_path = files[0]

        # 2. Ask user where to save the result
        save_path = choose_save_location(
            title="Choose Where to Save Output",
            default_filename="output.txt"
        )
        if not save_path:
            print("Operation cancelled. No save location chosen.")
            return

        try:
            # 3. [TODO: Write your tool's conversion or processing logic here!]
            with open(input_path, "r", encoding="utf-8", errors="replace") as f_in:
                data = f_in.read()

            with open(save_path, "w", encoding="utf-8") as f_out:
                f_out.write(data)

            # 4. Display professional success card
            print_success_card(
                operation="{name}",
                output_path=save_path,
                details={{
                    "Source": os.path.basename(input_path),
                    "Output": os.path.basename(save_path),
                    "Author": self.author
                }}
            )

            # 5. Prompt to open the output file
            try:
                ans = input(f"{{CYAN}}Open output file now? [y/N]: {{RESET}}").strip().lower()
                if ans in ("y", "yes"):
                    open_file_or_dir(save_path)
            except (KeyboardInterrupt, EOFError):
                pass

        except Exception as e:
            print_error_card(operation="{name}", error_message=str(e))
'''

def main():
    print("\n" + "=" * 65)
    print(" 🛠️  OPENFORGE TOOL SCAFFOLDER / GENERATOR")
    print(" Create a new pluggable tool for FileForge in 10 seconds!")
    print("=" * 65 + "\n")

    tool_name = input("👉 Tool Name (e.g., 'Markdown to PDF', 'Lab Report Formatter'): ").strip()
    if not tool_name:
        print("❌ Tool name is required.")
        sys.exit(1)

    default_id = slugify(tool_name)
    tool_id = input(f"👉 Tool ID [default: {default_id}]: ").strip() or default_id

    description = input("👉 Short Description: ").strip() or f"Community tool for {tool_name}"
    author = input("👉 Your GitHub Handle or Name [default: @Contributor]: ").strip() or "@Contributor"
    icon = input("👉 Emoji Icon [default: ⚡]: ").strip() or "⚡"
    category = input("👉 Category [default: ✨ COMMUNITY EXTENSIONS]: ").strip() or "✨ COMMUNITY EXTENSIONS"
    
    deps_raw = input("👉 Required pip packages (comma-separated, leave blank if none): ").strip()
    deps = [d.strip() for d in deps_raw.split(",") if d.strip()]

    words = [w.capitalize() for w in re.split(r'[^a-zA-Z0-9]', tool_name) if w]
    class_name = "".join(words) + "Tool"

    code = TEMPLATE.format(
        name=tool_name,
        tool_id=tool_id,
        description=description,
        author=author,
        icon=icon,
        category=category,
        dependencies=repr(deps),
        class_name=class_name
    )

    plugins_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plugins")
    os.makedirs(plugins_dir, exist_ok=True)
    target_file = os.path.join(plugins_dir, f"{tool_id}.py")

    if os.path.exists(target_file):
        overwrite = input(f"⚠️  File '{tool_id}.py' already exists. Overwrite? [y/N]: ").strip().lower()
        if overwrite not in ("y", "yes"):
            print("Aborted.")
            sys.exit(0)

    with open(target_file, "w", encoding="utf-8") as f:
        f.write(code)

    print("\n" + "─" * 65)
    print(f"🎉 SUCCESS! New tool created at:")
    print(f"   plugins/{tool_id}.py")
    print(f"\n👉 When you run 'python main.py', '{tool_name}' will automatically appear")
    print("   in your menu as a community tool!")
    print("─" * 65 + "\n")

if __name__ == "__main__":
    main()
