"""
template_manager.py - Manage script templates for different content types

Features:
- Create custom script templates
- List available templates
- Preview template output
- Import/export templates
- Template variables system

Usage:
    python template_manager.py --list
    python template_manager.py --create
    python template_manager.py --preview fact "quantum physics"
    python template_manager.py --export templates/
    python template_manager.py --import custom_template.json
"""

import json
import sys
from pathlib import Path
from typing import Dict, List
from datetime import datetime


class TemplateManager:
    """Manage script templates for reel generation"""
    
    DEFAULT_TEMPLATES = {
        "fact": {
            "name": "Interesting Fact",
            "description": "Share surprising facts",
            "variables": ["topic", "fact_1", "fact_2", "fact_3", "conclusion"],
            "structure": """Did you know about {topic}?

Here's something fascinating: {fact_1}

But wait, there's more. {fact_2}

And the most surprising part? {fact_3}

{conclusion}""",
            "example_output": "Did you know about the ocean? Here's something fascinating...",
            "tags": ["educational", "facts", "viral"]
        },
        
        "tutorial": {
            "name": "Quick Tutorial",
            "description": "Step-by-step how-to guide",
            "variables": ["topic", "hook", "step_1", "step_2", "step_3", "cta"],
            "structure": """{hook}

Here's how to master {topic}:

First: {step_1}

Next: {step_2}

Finally: {step_3}

{cta}""",
            "example_output": "Want to learn something new? Here's how to master...",
            "tags": ["tutorial", "educational", "howto"]
        },
        
        "story": {
            "name": "Narrative Story",
            "description": "Tell an engaging story",
            "variables": ["topic", "hook", "beginning", "middle", "twist", "conclusion"],
            "structure": """{hook}

Let me tell you about {topic}.

It all started when {beginning}

Then {middle}

But here's the twist: {twist}

{conclusion}""",
            "example_output": "You won't believe this story. Let me tell you about...",
            "tags": ["storytelling", "narrative", "engaging"]
        },
        
        "listicle": {
            "name": "Top List",
            "description": "Countdown or ranked list format",
            "variables": ["topic", "item_1", "item_2", "item_3", "item_4", "item_5"],
            "structure": """Top 5 {topic} you need to know:

Number 5: {item_5}

Number 4: {item_4}

Number 3: {item_3}

Number 2: {item_2}

And number 1: {item_1}

Now you know!""",
            "example_output": "Top 5 things you need to know...",
            "tags": ["list", "countdown", "viral"]
        },
        
        "myth_buster": {
            "name": "Myth vs Reality",
            "description": "Debunk common misconceptions",
            "variables": ["topic", "myth", "reality", "explanation", "conclusion"],
            "structure": """Think you know about {topic}? Think again.

MYTH: {myth}

REALITY: {reality}

Here's why: {explanation}

{conclusion}""",
            "example_output": "Think you know the truth? Let me blow your mind...",
            "tags": ["educational", "myth", "viral"]
        },
        
        "before_after": {
            "name": "Transformation Story",
            "description": "Show progress or change over time",
            "variables": ["topic", "before", "process", "after", "lesson"],
            "structure": """The transformation of {topic}

BEFORE: {before}

THE PROCESS: {process}

AFTER: {after}

The lesson? {lesson}""",
            "example_output": "Watch this incredible transformation...",
            "tags": ["transformation", "progress", "motivational"]
        },
        
        "comparison": {
            "name": "This vs That",
            "description": "Compare two things",
            "variables": ["item_a", "item_b", "difference_1", "difference_2", "verdict"],
            "structure": """{item_a} vs {item_b} - which is better?

Difference #1: {difference_1}

Difference #2: {difference_2}

The verdict: {verdict}

What do you think?""",
            "example_output": "The ultimate comparison you've been waiting for...",
            "tags": ["comparison", "versus", "debate"]
        },
        
        "hook_driven": {
            "name": "Viral Hook Format",
            "description": "Attention-grabbing opening",
            "variables": ["hook", "reveal_1", "reveal_2", "punchline", "cta"],
            "structure": """STOP SCROLLING! {hook}

Here's what nobody tells you: {reveal_1}

And get this: {reveal_2}

The punchline? {punchline}

{cta}""",
            "example_output": "STOP SCROLLING! You need to hear this...",
            "tags": ["viral", "hook", "attention"]
        }
    }
    
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(exist_ok=True)
        
        # Load custom templates
        self.templates = self.DEFAULT_TEMPLATES.copy()
        self.load_custom_templates()
    
    def load_custom_templates(self):
        """Load custom templates from JSON files"""
        for template_file in self.templates_dir.glob("*.json"):
            try:
                with open(template_file, 'r') as f:
                    custom = json.load(f)
                    template_id = template_file.stem
                    self.templates[template_id] = custom
                    print(f"✅ Loaded custom template: {template_id}")
            except Exception as e:
                print(f"⚠️  Failed to load {template_file}: {str(e)}")
    
    def list_templates(self):
        """Display all available templates"""
        print(f"\n{'='*70}")
        print(f"📋 AVAILABLE SCRIPT TEMPLATES ({len(self.templates)})")
        print(f"{'='*70}\n")
        
        for template_id, template in self.templates.items():
            name = template.get("name", template_id)
            desc = template.get("description", "No description")
            tags = ", ".join(template.get("tags", []))
            
            print(f"🎬 {template_id}")
            print(f"   Name: {name}")
            print(f"   Description: {desc}")
            print(f"   Tags: {tags}")
            print(f"   Variables: {', '.join(template.get('variables', []))}")
            print()
    
    def preview_template(self, template_id: str, topic: str = "example topic"):
        """Preview template with example data"""
        
        if template_id not in self.templates:
            print(f"❌ Template '{template_id}' not found")
            return
        
        template = self.templates[template_id]
        structure = template.get("structure", "")
        variables = template.get("variables", [])
        
        # Create example data
        example_data = {var: f"[{var.replace('_', ' ').upper()}]" for var in variables}
        example_data["topic"] = topic
        
        try:
            output = structure.format(**example_data)
            
            print(f"\n{'='*60}")
            print(f"🎬 TEMPLATE PREVIEW: {template['name']}")
            print(f"{'='*60}\n")
            print(output)
            print(f"\n{'='*60}\n")
            
        except KeyError as e:
            print(f"❌ Error: Missing variable {e}")
    
    def create_interactive(self):
        """Interactive template creation wizard"""
        
        print(f"\n{'='*60}")
        print(f"🎨 CREATE NEW TEMPLATE")
        print(f"{'='*60}\n")
        
        # Get basic info
        template_id = input("Template ID (lowercase, no spaces): ").strip().lower().replace(" ", "_")
        
        if not template_id:
            print("❌ Template ID required")
            return
        
        if template_id in self.templates:
            overwrite = input(f"⚠️  Template '{template_id}' exists. Overwrite? (y/n): ")
            if overwrite.lower() != 'y':
                return
        
        name = input("Template Name: ").strip()
        description = input("Description: ").strip()
        tags = input("Tags (comma-separated): ").strip().split(",")
        tags = [t.strip() for t in tags if t.strip()]
        
        # Define variables
        print("\nDefine template variables (type 'done' when finished):")
        variables = []
        
        while True:
            var = input(f"  Variable {len(variables)+1}: ").strip()
            if var.lower() == 'done':
                break
            if var:
                variables.append(var)
        
        # Create structure
        print("\nEnter template structure (use {variable_name} for variables):")
        print("Press Ctrl+D (Unix) or Ctrl+Z then Enter (Windows) when done.\n")
        
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        
        structure = "\n".join(lines)
        
        # Create template
        new_template = {
            "name": name,
            "description": description,
            "variables": variables,
            "structure": structure,
            "tags": tags,
            "created": datetime.now().isoformat()
        }
        
        # Save to file
        filename = self.templates_dir / f"{template_id}.json"
        with open(filename, 'w') as f:
            json.dump(new_template, f, indent=2)
        
        self.templates[template_id] = new_template
        
        print(f"\n✅ Template created: {filename}")
        print(f"\nUse with: python main.py --template {template_id} 'your prompt'")
    
    def export_template(self, template_id: str, output_path: str = None):
        """Export template to JSON file"""
        
        if template_id not in self.templates:
            print(f"❌ Template '{template_id}' not found")
            return
        
        if not output_path:
            output_path = f"{template_id}_template.json"
        
        template = self.templates[template_id]
        
        with open(output_path, 'w') as f:
            json.dump(template, f, indent=2)
        
        print(f"✅ Template exported: {output_path}")
    
    def import_template(self, filepath: str):
        """Import template from JSON file"""
        
        try:
            with open(filepath, 'r') as f:
                template = json.load(f)
            
            # Validate template structure
            required_fields = ["name", "structure", "variables"]
            if not all(field in template for field in required_fields):
                print(f"❌ Invalid template format. Required: {required_fields}")
                return
            
            # Get template ID from filename
            template_id = Path(filepath).stem
            
            # Save to templates directory
            output_path = self.templates_dir / f"{template_id}.json"
            with open(output_path, 'w') as f:
                json.dump(template, f, indent=2)
            
            self.templates[template_id] = template
            
            print(f"✅ Template imported: {template_id}")
            
        except Exception as e:
            print(f"❌ Import failed: {str(e)}")
    
    def export_all(self, output_dir: str = "template_backup"):
        """Export all templates to directory"""
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        for template_id, template in self.templates.items():
            filename = output_path / f"{template_id}.json"
            with open(filename, 'w') as f:
                json.dump(template, f, indent=2)
        
        print(f"✅ Exported {len(self.templates)} templates to {output_dir}")
    
    def search_templates(self, query: str):
        """Search templates by name, description, or tags"""
        
        query = query.lower()
        results = []
        
        for template_id, template in self.templates.items():
            name = template.get("name", "").lower()
            desc = template.get("description", "").lower()
            tags = " ".join(template.get("tags", [])).lower()
            
            if query in name or query in desc or query in tags or query in template_id:
                results.append((template_id, template))
        
        if not results:
            print(f"❌ No templates found matching '{query}'")
            return
        
        print(f"\n🔍 Found {len(results)} template(s) matching '{query}':\n")
        
        for template_id, template in results:
            name = template.get("name", template_id)
            desc = template.get("description", "No description")
            print(f"  • {template_id} - {name}")
            print(f"    {desc}\n")


def main():
    """Main entry point"""
    
    manager = TemplateManager()
    
    if len(sys.argv) < 2:
        print("""
Usage:
    python template_manager.py --list                        # List all templates
    python template_manager.py --create                      # Create new template
    python template_manager.py --preview <template_id>       # Preview template
    python template_manager.py --export <template_id>        # Export template
    python template_manager.py --export-all                  # Export all templates
    python template_manager.py --import <file.json>          # Import template
    python template_manager.py --search <query>              # Search templates
    
Examples:
    python template_manager.py --list
    python template_manager.py --preview fact "quantum physics"
    python template_manager.py --create
    python template_manager.py --search viral
        """)
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == "--list" or command == "-l":
        manager.list_templates()
    
    elif command == "--create" or command == "-c":
        manager.create_interactive()
    
    elif command == "--preview" or command == "-p":
        if len(sys.argv) < 3:
            print("❌ Usage: --preview <template_id> [topic]")
            sys.exit(1)
        
        template_id = sys.argv[2]
        topic = sys.argv[3] if len(sys.argv) > 3 else "example topic"
        manager.preview_template(template_id, topic)
    
    elif command == "--export" or command == "-e":
        if len(sys.argv) < 3:
            print("❌ Usage: --export <template_id> [output_path]")
            sys.exit(1)
        
        template_id = sys.argv[2]
        output_path = sys.argv[3] if len(sys.argv) > 3 else None
        manager.export_template(template_id, output_path)
    
    elif command == "--export-all":
        output_dir = sys.argv[2] if len(sys.argv) > 2 else "template_backup"
        manager.export_all(output_dir)
    
    elif command == "--import" or command == "-i":
        if len(sys.argv) < 3:
            print("❌ Usage: --import <file.json>")
            sys.exit(1)
        
        filepath = sys.argv[2]
        manager.import_template(filepath)
    
    elif command == "--search" or command == "-s":
        if len(sys.argv) < 3:
            print("❌ Usage: --search <query>")
            sys.exit(1)
        
        query = sys.argv[2]
        manager.search_templates(query)
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Run without arguments to see usage")
        sys.exit(1)


if __name__ == "__main__":
    main()