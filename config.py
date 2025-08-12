"""
RepoPulse Configuration
Dynamic configuration for repository analysis and AI detection
"""

import os
import json
from typing import Dict, List, Any

class RepoPulseConfig:
    """Dynamic configuration manager for RepoPulse"""
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file or "repopulse_config.json"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
        
        # Return default configuration
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "name_mappings": {
                "normalization_rules": [
                    {
                        "pattern": r'\s+',
                        "replacement": "",
                        "description": "Remove spaces for name matching"
                    }
                ],
                "known_mappings": {
                    "sonikumari": "Soni Kumari",
                    "mukundsingh": "Mukund Singh",
                    "vaibhavbhatia": "Vaibhav Bhatia",
                    "siddharthvatsal": "Siddharth Vatsal",
                    "shiwanshukashyap": "Shiwanshu Kashyap",
                    "nidhibansal": "Nidhi Bansal",
                    "nikhilmanglik": "Nikhil Manglik",
                    "akashgupta1": "Akash Gupta",
                    "jainagpal": "Jai Nagpal",
                    "jainagpal1": "Jai Nagpal",
                    "jainagpal2": "Jai Nagpal"
                }
            },
            "file_types": {
                "code_extensions": [
                    ".cs", ".js", ".ts", ".py", ".java", ".cpp", ".c", ".h",
                    ".php", ".rb", ".go", ".swift", ".kt", ".scala", ".rs",
                    ".jsx", ".tsx", ".vue", ".svelte", ".r", ".m", ".mm"
                ],
                "exclude_patterns": [
                    ".config", ".json", ".xml", ".md", ".txt", ".yml", ".yaml",
                    ".lock", ".log", ".gitignore", ".editorconfig", ".env",
                    ".min.js", ".min.css", ".map", ".d.ts"
                ],
                "config_files": [
                    "package.json", "requirements.txt", "pom.xml", "build.gradle",
                    "webpack.config.js", "tsconfig.json", ".eslintrc", "dockerfile"
                ]
            },
            "ai_detection": {
                "confidence_thresholds": {
                    "high": 0.8,
                    "medium": 0.6,
                    "low": 0.4,
                    "minimum": 0.25
                },
                "keywords": {
                    "high_confidence": [
                        "cursor", "copilot", "chatgpt", "gpt", "claude", "bard", "gemini",
                        "ai generated", "ai-assisted", "ai helped", "ai suggested",
                        "auto-generated", "generated code", "boilerplate"
                    ],
                    "medium_confidence": [
                        "intellisense", "autocomplete", "code completion",
                        "assisted", "helped by", "suggested by", "generated"
                    ],
                    "low_confidence": [
                        "refactor", "optimize", "improve", "enhance", "update",
                        "fix", "bug", "feature", "implement", "complete"
                    ]
                },
                "patterns": {
                    "commit_message_patterns": [
                        r"ai\s+generated",
                        r"generated\s+by\s+ai",
                        r"cursor\s+assisted",
                        r"copilot\s+suggestion",
                        r"auto\s+generated"
                    ],
                    "file_content_patterns": [
                        r"//\s*Generated\s+by\s+AI",
                        r"<!--\s*AI\s+Generated\s*-->",
                        r"#\s*AI\s+Generated",
                        r"//\s*Cursor\s+assisted"
                    ]
                }
            },
            "git_commands": {
                "log_format": "%H|%an|%ad|%s",
                "date_format": "short",
                "numstat": True,
                "timeout": 30
            },
            "analysis": {
                "max_repositories": 50,
                "max_commits_per_repo": 10000,
                "date_range_limit_days": 3650,  # 10 years
                "batch_size": 100
            },
            "server": {
                "host": "0.0.0.0",
                "port": 5001,
                "debug": False,
                "cors_origins": ["*"]
            }
        }
    
    def save_config(self) -> bool:
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> bool:
        """Set configuration value by key (supports dot notation)"""
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        return True
    
    def add_name_mapping(self, normalized_name: str, display_name: str) -> bool:
        """Add a new name mapping"""
        self.config["name_mappings"]["known_mappings"][normalized_name] = display_name
        return self.save_config()
    
    def add_code_extension(self, extension: str) -> bool:
        """Add a new code file extension"""
        if extension not in self.config["file_types"]["code_extensions"]:
            self.config["file_types"]["code_extensions"].append(extension)
            return self.save_config()
        return True
    
    def add_exclude_pattern(self, pattern: str) -> bool:
        """Add a new exclude pattern"""
        if pattern not in self.config["file_types"]["exclude_patterns"]:
            self.config["file_types"]["exclude_patterns"].append(pattern)
            return self.save_config()
        return True
    
    def add_ai_keyword(self, keyword: str, confidence_level: str = "medium") -> bool:
        """Add a new AI detection keyword"""
        if confidence_level in self.config["ai_detection"]["keywords"]:
            if keyword not in self.config["ai_detection"]["keywords"][confidence_level]:
                self.config["ai_detection"]["keywords"][confidence_level].append(keyword)
                return self.save_config()
        return False
    
    def get_name_mappings(self) -> Dict[str, str]:
        """Get all name mappings"""
        return self.config["name_mappings"]["known_mappings"]
    
    def get_code_extensions(self) -> List[str]:
        """Get all code file extensions"""
        return self.config["file_types"]["code_extensions"]
    
    def get_exclude_patterns(self) -> List[str]:
        """Get all exclude patterns"""
        return self.config["file_types"]["exclude_patterns"]
    
    def get_ai_keywords(self, confidence_level: str = None) -> Dict[str, List[str]]:
        """Get AI keywords by confidence level or all"""
        if confidence_level:
            return self.config["ai_detection"]["keywords"].get(confidence_level, [])
        return self.config["ai_detection"]["keywords"]
    
    def reload(self) -> bool:
        """Reload configuration from file"""
        self.config = self._load_config()
        return True

# Global configuration instance
config = RepoPulseConfig() 