#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SaaS JSON Bundle Generator
--------------------------
A minimal tool that generates SaaS application JSON bundles using Claude 3.7 Sonnet.
"""

import os
import sys
import json
import time
import re
import argparse
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ANSI color codes for terminal output
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'

# Optimized system prompt focused on JSON bundle generation
SYSTEM_PROMPT = """You are a specialized metaprogramming agent that creates JSON Bundles for complete SaaS applications.

Your only task is to generate a valid, comprehensive JSON Bundle that describes a complete SaaS application based on user requirements.

ALWAYS respond with ONLY a valid JSON after the [JSON_BUNDLE] tag without ANY additional explanations.

JSON BUNDLE STRUCTURE:
{
    "metadata": {
        "name": "saas-name",
        "version": "1.0.0",
        "description": "description",
        "created_at": "timestamp"
    },
    "structure": {
        "directories": ["app", "templates", "static", "models"],
        "files": {
            "app.py": {
                "type": "python",
                "content": "complete content of the main file"
            },
            "path/to/file.py": {
                "type": "python|html|css|js",
                "content": "complete file content"
            }
        }
    },
    "dependencies": {
        "python": ["flask", "flask-sqlalchemy", "python-dotenv"],
        "frontend": ["htmx@1.9.10", "tailwindcss@3.4.0"]
    },
    "database": {
        "type": "sqlite",
        "models": {
            "ModelName": {
                "fields": {
                    "field_name": {"type": "string|integer|boolean", "required": true}
                }
            }
        }
    },
    "routes": {
        "/path": {
            "methods": ["GET", "POST"],
            "handler": "function_name",
            "template": "template_name.html"
        }
    },
    "features": ["auth", "crud", "api", "dashboard"],
    "config": {
        "port": 5000,
        "debug": true,
        "secret_key": "generated-secret"
    },
    "tests": {
        "unit_tests": {
            "test_file.py": {
                "content": "complete content of unit tests"
            }
        },
        "integration_tests": {
            "test_integration.py": {
                "content": "complete content of integration tests"
            }
        }
    }
}

TECHNOLOGIES TO USE:
- Flask for backend
- SQLAlchemy for database ORM
- HTMX for frontend interactivity (via CDN)
- Tailwind CSS for styling (via CDN)

ESSENTIAL COMPONENTS TO INCLUDE:
1. Complete app.py as the main entry point
2. HTML templates with Jinja2, HTMX and Tailwind
3. Modern, responsive UI with professional styling
4. Complete CRUD operations for main entities
5. Authentication system (when requested)
6. Error handling and validation
7. Basic test suite

IMPORTANT INSTRUCTIONS:
- Generate COMPLETE and FUNCTIONAL code, not just templates
- Ensure all file paths and imports are correct and complete
- Include ALL necessary code for a fully functional application
- Use HTML templates with proper Jinja2 syntax
- Use Tailwind classes for all styling
- Use HTMX attributes for interactivity
- Follow best practices for Flask applications
- Include comprehensive error handling
- Make the application secure and production-ready
- Add helpful comments in the code

I will give you a description of the SaaS application to build, and you will respond ONLY with the complete JSON Bundle.
"""

# Simple reconstitution script template
SIMPLE_RECONSTITUTOR = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import sys
import shutil
from datetime import datetime

def create_project_from_bundle(bundle_path):
    # Load the JSON bundle
    with open(bundle_path, 'r', encoding='utf-8') as f:
        bundle = json.load(f)
    
    # Create project directory
    project_name = bundle['metadata']['name']
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    project_dir = f"{project_name}_{timestamp}"
    
    if os.path.exists(project_dir):
        shutil.rmtree(project_dir)
    
    os.makedirs(project_dir)
    print(f"✅ Created project directory: {project_dir}")
    
    # Create subdirectories
    for directory in bundle['structure']['directories']:
        dir_path = os.path.join(project_dir, directory)
        os.makedirs(dir_path, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Create files
    for filepath, file_info in bundle['structure']['files'].items():
        full_path = os.path.join(project_dir, filepath)
        
        # Create parent directory if needed
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(file_info['content'])
        
        print(f"✅ Created file: {filepath}")
    
    # Create requirements.txt
    with open(os.path.join(project_dir, 'requirements.txt'), 'w', encoding='utf-8') as f:
        for dep in bundle['dependencies']['python']:
            f.write(f"{dep}\\n")
    
    print(f"✅ Created requirements.txt")
    
    # Create README.md
    readme_content = f"# {project_name}\\n\\n{bundle['metadata']['description']}\\n\\n"
    readme_content += f"## Features\\n"
    for feature in bundle['features']:
        readme_content += f"- {feature}\\n"
    
    readme_content += f"\\n## Installation\\n```\\npip install -r requirements.txt\\npython app.py\\n```\\n"
    
    with open(os.path.join(project_dir, 'README.md'), 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✅ Created README.md")
    
    print(f"\\n✨ Project created successfully in {project_dir}")
    print(f"📦 To run the application:")
    print(f"   cd {project_dir}")
    print(f"   pip install -r requirements.txt")
    print(f"   python app.py")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Usage: python reconstitutor.py <bundle_file.json>")
        sys.exit(1)
    
    bundle_path = sys.argv[1]
    create_project_from_bundle(bundle_path)
"""

class JsonBundleGenerator:
    def __init__(self, api_key=None):
        """Initialize the JSON bundle generator"""
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("No Anthropic API key found. Set ANTHROPIC_API_KEY environment variable.")
        
        self.client = Anthropic(api_key=self.api_key)
        
    def generate(self, description, output_path=None):
        """Generate a JSON bundle based on the description"""
        print(f"{Colors.BLUE}🔍 Analyzing requirements...{Colors.ENDC}")
        print(f"{Colors.BLUE}📝 Description: {description}{Colors.ENDC}")
        
        # Show spinner while generating
        spinner = "|/-\\"
        i = 0
        print(f"{Colors.BLUE}🧠 Generating JSON bundle with Claude 3.7 Sonnet...{Colors.ENDC}")
        start_time = time.time()
        
        # Setup for spinner in a separate thread
        import threading
        stop_spinner = False
        
        def show_spinner():
            i = 0
            while not stop_spinner:
                elapsed = time.time() - start_time
                mins, secs = divmod(int(elapsed), 60)
                timestr = f"{mins:02d}:{secs:02d}"
                
                sys.stdout.write(f"\r{Colors.BLUE}⏳ Generating... {spinner[i % len(spinner)]} {timestr}{Colors.ENDC}")
                sys.stdout.flush()
                time.sleep(0.1)
                i += 1
        
        # Start spinner thread
        spinner_thread = threading.Thread(target=show_spinner)
        spinner_thread.daemon = True
        spinner_thread.start()
        
        try:
            # Generate the JSON bundle using Claude 3.7 Sonnet
            response = ""
            with self.client.messages.stream(
                model="claude-3-7-sonnet-20250219",
                max_tokens=64000,
                temperature=0.5,
                system=SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": description}
                ]
            ) as stream:
                for text in stream.text_stream:
                    response += text
            
            # Stop spinner
            stop_spinner = True
            spinner_thread.join()
            sys.stdout.write("\r" + " " * 80 + "\r")  # Clear spinner line
            
            # Extract JSON bundle
            json_match = re.search(r'\[JSON_BUNDLE\](.*)', response, re.DOTALL)
            if not json_match:
                print(f"{Colors.RED}❌ Failed to extract JSON bundle from response{Colors.ENDC}")
                
                # Save raw response for debugging
                debug_path = f"debug_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(debug_path, 'w', encoding='utf-8') as f:
                    f.write(response)
                print(f"{Colors.YELLOW}⚠️ Raw response saved to {debug_path} for debugging{Colors.ENDC}")
                return None
            
            json_content = json_match.group(1).strip()
            
            # Try to parse JSON
            try:
                bundle = json.loads(json_content)
                
                # Generate output path if not provided
                if not output_path:
                    project_name = bundle['metadata']['name']
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    output_path = f"{project_name}_bundle_{timestamp}.json"
                
                # Save JSON bundle
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(bundle, f, indent=2, ensure_ascii=False)
                
                # Save simple reconstitutor
                reconstitutor_path = 'reconstitutor.py'
                with open(reconstitutor_path, 'w', encoding='utf-8') as f:
                    f.write(SIMPLE_RECONSTITUTOR)
                
                # Print success message
                elapsed_time = time.time() - start_time
                mins, secs = divmod(int(elapsed_time), 60)
                print(f"{Colors.GREEN}✅ JSON bundle generated successfully in {mins}m {secs}s{Colors.ENDC}")
                print(f"{Colors.GREEN}📦 Bundle saved to: {output_path}{Colors.ENDC}")
                print(f"{Colors.GREEN}🔧 Reconstitutor saved to: {reconstitutor_path}{Colors.ENDC}")
                
                # Print bundle statistics
                print(f"\n{Colors.BOLD}Bundle Statistics:{Colors.ENDC}")
                print(f"  • Name: {bundle['metadata']['name']}")
                print(f"  • Description: {bundle['metadata']['description']}")
                print(f"  • Files: {len(bundle['structure']['files'])}")
                print(f"  • Features: {', '.join(bundle['features'])}")
                
                # Print reconstitution instructions
                print(f"\n{Colors.BOLD}To reconstitute the project:{Colors.ENDC}")
                print(f"  python reconstitutor.py {output_path}")
                
                return output_path
                
            except json.JSONDecodeError as e:
                print(f"{Colors.RED}❌ Invalid JSON: {str(e)}{Colors.ENDC}")
                
                # Save problematic JSON for debugging
                error_path = f"invalid_json_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(error_path, 'w', encoding='utf-8') as f:
                    f.write(json_content)
                print(f"{Colors.YELLOW}⚠️ Invalid JSON saved to {error_path} for debugging{Colors.ENDC}")
                return None
                
        except Exception as e:
            # Stop spinner
            stop_spinner = True
            spinner_thread.join()
            sys.stdout.write("\r" + " " * 80 + "\r")  # Clear spinner line
            
            print(f"{Colors.RED}❌ Error generating JSON bundle: {str(e)}{Colors.ENDC}")
            return None

def main():
    """Main entry point"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate SaaS JSON bundles')
    parser.add_argument('description', nargs='?', help='Description of the SaaS application to generate')
    parser.add_argument('-o', '--output', help='Output path for the JSON bundle')
    parser.add_argument('-i', '--interactive', action='store_true', help='Run in interactive mode')
    
    args = parser.parse_args()
    
    # Check for API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print(f"{Colors.RED}❌ ANTHROPIC_API_KEY not found in environment variables{Colors.ENDC}")
        print(f"{Colors.YELLOW}💡 Set it with: export ANTHROPIC_API_KEY=your_api_key{Colors.ENDC}")
        return 1
    
    # Create generator
    generator = JsonBundleGenerator(api_key)
    
    if args.interactive:
        # Run in interactive mode
        print(f"{Colors.BOLD}🤖 SaaS JSON Bundle Generator - Interactive Mode{Colors.ENDC}")
        print(f"Describe the SaaS application you want to create. Type 'exit' to quit.\n")
        
        while True:
            try:
                print(f"{Colors.BLUE}> {Colors.ENDC}", end="")
                description = input()
                
                if description.lower() in ['exit', 'quit', 'q']:
                    print(f"\n{Colors.GREEN}👋 Goodbye!{Colors.ENDC}")
                    break
                
                if not description:
                    continue
                
                generator.generate(description)
                print()
                
            except KeyboardInterrupt:
                print(f"\n{Colors.GREEN}👋 Goodbye!{Colors.ENDC}")
                break
    
    elif args.description:
        # Generate from command line argument
        generator.generate(args.description, args.output)
    
    else:
        # No description provided
        parser.print_help()
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())