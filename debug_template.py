#!/usr/bin/env python3
"""
Debug script to check the template content
"""

from report_generator import RepoPulseReportGenerator

def debug_template():
    """Check the template content"""
    generator = RepoPulseReportGenerator()
    
    # Get the template content by looking at the method
    import inspect
    source = inspect.getsource(generator.generate_html_report)
    
    # Find the template string
    start = source.find('html_template = """')
    if start != -1:
        start += len('html_template = """')
        end = source.find('"""', start)
        if end != -1:
            template = source[start:end]
            
            # Check for AI Commits references
            if 'AI Commits' in template:
                print("❌ AI Commits found in template!")
                lines = template.split('\n')
                for i, line in enumerate(lines):
                    if 'AI Commits' in line:
                        print(f"Line {i+1}: {line.strip()}")
            else:
                print("✅ No AI Commits found in template")
                
            # Check for total_ai_commits
            if 'total_ai_commits' in template:
                print("❌ total_ai_commits found in template!")
            else:
                print("✅ No total_ai_commits found in template")
        else:
            print("❌ Could not find end of template")
    else:
        print("❌ Could not find template string")

if __name__ == "__main__":
    debug_template() 