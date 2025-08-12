#!/usr/bin/env python3
"""
Direct test to check the template being used
"""

import sys
sys.path.append('.')

from report_generator import report_generator
import inspect

def test_template_direct():
    """Test the template directly"""
    
    # Get the source code of the method
    source = inspect.getsource(report_generator.generate_html_report)
    
    # Find the template string
    start = source.find('html_template = """')
    if start != -1:
        start += len('html_template = """')
        end = source.find('"""', start)
        if end != -1:
            template = source[start:end]
            
            print("Template analysis:")
            print(f"Template length: {len(template)}")
            
            # Check for specific patterns
            patterns = [
                'AI Commits',
                'total_ai_commits',
                'repo.totalAICommits',
                'dev.aiCommits'
            ]
            
            for pattern in patterns:
                if pattern in template:
                    print(f"❌ Found '{pattern}' in template")
                    # Find the line numbers
                    lines = template.split('\n')
                    for i, line in enumerate(lines):
                        if pattern in line:
                            print(f"  Line {i+1}: {line.strip()}")
                else:
                    print(f"✅ No '{pattern}' found in template")
            
            # Check the summary section specifically
            if 'stat-card' in template:
                summary_start = template.find('stats-grid')
                if summary_start != -1:
                    summary_end = template.find('</div>', summary_start)
                    if summary_end != -1:
                        summary_section = template[summary_start:summary_end]
                        print(f"\nSummary section contains 'AI Commits': {'AI Commits' in summary_section}")
                        if 'AI Commits' in summary_section:
                            print("Summary section:")
                            print(summary_section)
        else:
            print("❌ Could not find end of template")
    else:
        print("❌ Could not find template string")

if __name__ == "__main__":
    test_template_direct() 