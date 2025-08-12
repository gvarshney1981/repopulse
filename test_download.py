#!/usr/bin/env python3
"""
Test script to reproduce the download error
"""

import requests
import json

def test_download_error():
    """Test the download endpoint with sample data to reproduce the error"""
    
    # Sample data that might be causing the issue
    test_data = {
        "results": [
            {
                "name": "test-repo",
                "path": "/path/to/test-repo",
                "startDate": "2024-01-01",
                "endDate": "2024-12-31",
                "totalCommits": 100,
                "totalLinesAdded": 1000,
                "totalLinesRemoved": 200,
                "totalAiLinesAdded": 150,
                "totalAiLinesRemoved": 30,
                "totalAiCommits": 25,
                "overallAiPercentage": 15.0,
                "developerStats": [
                    {
                        "name": "John Doe",
                        "commits": 50,
                        "linesAdded": 500,
                        "linesRemoved": 100,
                        "aiLinesAdded": 75,
                        "aiLinesRemoved": 15,
                        "aiCommits": 12,
                        "aiPercentage": 15.0
                    }
                ],
                "timeSeriesData": []
            }
        ],
        "totalRepos": 1,
        "validRepos": 1,
        "startDate": "2024-01-01",
        "endDate": "2024-12-31"
    }
    
    try:
        # Test the download endpoint
        response = requests.post(
            'http://localhost:5002/api/download/html',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Download successful!")
            # Save the downloaded file
            with open('downloaded_report.html', 'wb') as f:
                f.write(response.content)
            print("Report saved as 'downloaded_report.html'")
        else:
            print(f"❌ Download failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("Testing download endpoint...")
    test_download_error() 