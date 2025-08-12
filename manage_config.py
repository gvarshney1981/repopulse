#!/usr/bin/env python3
"""
RepoPulse Configuration Manager
Interactive tool to manage RepoPulse configuration
"""

import json
import sys
from config import config

def print_banner():
    """Print the configuration manager banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║                🫀 RepoPulse Config Manager 🫀               ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def show_menu():
    """Show the main menu"""
    menu = """
    📋 Configuration Management Options:
    
    1. 📖 View current configuration
    2. ✏️  Edit configuration
    3. 👤 Add name mapping
    4. 🤖 Add AI keyword
    5. 📁 Add code file extension
    6. 🚫 Add exclude pattern
    7. 💾 Save configuration
    8. 🔄 Reload configuration
    9. 📊 Show statistics
    0. 🚪 Exit
    
    Enter your choice (0-9): """
    return input(menu)

def view_config():
    """View current configuration"""
    print("\n📖 Current Configuration:")
    print("=" * 50)
    print(json.dumps(config.config, indent=2))
    print("=" * 50)

def edit_config():
    """Edit configuration interactively"""
    print("\n✏️  Edit Configuration")
    print("Available sections:")
    sections = list(config.config.keys())
    for i, section in enumerate(sections, 1):
        print(f"  {i}. {section}")
    
    try:
        choice = int(input("\nSelect section to edit (0 to cancel): "))
        if choice == 0:
            return
        if 1 <= choice <= len(sections):
            section = sections[choice - 1]
            edit_section(section)
        else:
            print("❌ Invalid choice")
    except ValueError:
        print("❌ Please enter a valid number")

def edit_section(section):
    """Edit a specific configuration section"""
    print(f"\nEditing section: {section}")
    current_value = config.config[section]
    print(f"Current value: {json.dumps(current_value, indent=2)}")
    
    try:
        new_value_str = input("Enter new value (JSON format, or 'cancel'): ")
        if new_value_str.lower() == 'cancel':
            return
        
        new_value = json.loads(new_value_str)
        config.config[section] = new_value
        print("✅ Section updated")
    except json.JSONDecodeError:
        print("❌ Invalid JSON format")
    except Exception as e:
        print(f"❌ Error: {e}")

def add_name_mapping():
    """Add a new name mapping"""
    print("\n👤 Add Name Mapping")
    normalized_name = input("Enter normalized name (e.g., 'johndoe'): ").strip()
    display_name = input("Enter display name (e.g., 'John Doe'): ").strip()
    
    if normalized_name and display_name:
        if config.add_name_mapping(normalized_name, display_name):
            print(f"✅ Name mapping added: {normalized_name} -> {display_name}")
        else:
            print("❌ Failed to add name mapping")
    else:
        print("❌ Both names are required")

def add_ai_keyword():
    """Add a new AI keyword"""
    print("\n🤖 Add AI Keyword")
    keyword = input("Enter keyword: ").strip()
    print("Confidence levels: high, medium, low")
    confidence = input("Enter confidence level (default: medium): ").strip() or "medium"
    
    if keyword:
        if config.add_ai_keyword(keyword, confidence):
            print(f"✅ AI keyword added: {keyword} (confidence: {confidence})")
        else:
            print("❌ Failed to add AI keyword")
    else:
        print("❌ Keyword is required")

def add_code_extension():
    """Add a new code file extension"""
    print("\n📁 Add Code File Extension")
    extension = input("Enter file extension (e.g., '.dart'): ").strip()
    
    if extension:
        if config.add_code_extension(extension):
            print(f"✅ Code extension added: {extension}")
        else:
            print("❌ Failed to add code extension")
    else:
        print("❌ Extension is required")

def add_exclude_pattern():
    """Add a new exclude pattern"""
    print("\n🚫 Add Exclude Pattern")
    pattern = input("Enter exclude pattern (e.g., '.min.js'): ").strip()
    
    if pattern:
        if config.add_exclude_pattern(pattern):
            print(f"✅ Exclude pattern added: {pattern}")
        else:
            print("❌ Failed to add exclude pattern")
    else:
        print("❌ Pattern is required")

def save_config():
    """Save configuration to file"""
    if config.save_config():
        print("✅ Configuration saved successfully")
    else:
        print("❌ Failed to save configuration")

def reload_config():
    """Reload configuration from file"""
    if config.reload():
        print("✅ Configuration reloaded successfully")
    else:
        print("❌ Failed to reload configuration")

def show_statistics():
    """Show configuration statistics"""
    print("\n📊 Configuration Statistics:")
    print("=" * 40)
    
    name_mappings = config.get_name_mappings()
    code_extensions = config.get_code_extensions()
    exclude_patterns = config.get_exclude_patterns()
    ai_keywords = config.get_ai_keywords()
    
    print(f"👤 Name mappings: {len(name_mappings)}")
    print(f"📁 Code extensions: {len(code_extensions)}")
    print(f"🚫 Exclude patterns: {len(exclude_patterns)}")
    print(f"🤖 AI keywords:")
    for level, keywords in ai_keywords.items():
        print(f"   - {level}: {len(keywords)} keywords")
    
    print(f"💾 Config file: {config.config_file}")
    print("=" * 40)

def main():
    """Main function"""
    print_banner()
    
    while True:
        try:
            choice = show_menu()
            
            if choice == '1':
                view_config()
            elif choice == '2':
                edit_config()
            elif choice == '3':
                add_name_mapping()
            elif choice == '4':
                add_ai_keyword()
            elif choice == '5':
                add_code_extension()
            elif choice == '6':
                add_exclude_pattern()
            elif choice == '7':
                save_config()
            elif choice == '8':
                reload_config()
            elif choice == '9':
                show_statistics()
            elif choice == '0':
                print("\n👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please try again.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main() 