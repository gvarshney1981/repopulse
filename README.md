# RepoPulse

A professional web application to analyze developer contributions and AI-generated code detection across multiple Git repositories. Track lines of code written, commits, developer productivity, and AI assistance with beautiful visualizations.

## Features

- 📊 **Multi-repository analysis** - Analyze multiple Git repositories at once
- 👥 **Developer statistics** - Track individual developer contributions
- 📈 **Visual charts** - Beautiful charts showing contribution patterns
- 📅 **Date range filtering** - Analyze specific time periods
- 🎯 **Combined statistics** - Aggregate data across all repositories
- 📱 **Responsive design** - Works on desktop and mobile devices

## Screenshots

The application provides:
- Summary cards with key metrics
- Individual repository analysis with charts
- Combined developer statistics across all repositories
- Interactive tables and visualizations

## Installation

### Prerequisites

- Python 3.7+
- Git installed and accessible from command line
- Web browser

### Setup

1. **Clone or download the project:**
   ```bash
   cd RepoPulse
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the backend server:**
   ```bash
   # Option 1: Use the startup script
   python3 start_repopulse.py
   
   # Option 2: Direct server start
   python3 server.py
   ```
   The server will start on `http://localhost:5001`

4. **Open the web application:**
   - Open `index.html` in your web browser
   - Or serve it using a local web server

### Configuration Management

RepoPulse uses a dynamic configuration system that can be managed through:

1. **Interactive Configuration Manager:**
   ```bash
   python3 manage_config.py
   ```

2. **API Endpoints:**
   - `GET /api/config` - View current configuration
   - `POST /api/config` - Update configuration
   - `POST /api/config/name-mappings` - Add name mappings
   - `POST /api/config/ai-keywords` - Add AI keywords
   - `POST /api/config/reload` - Reload configuration

3. **Configuration File:**
   - `repopulse_config.json` - JSON configuration file
   - Automatically created on first run
   - Can be edited manually or through the API

### Report Generation

RepoPulse can generate professional HTML reports:

**HTML Reports:**
- Interactive web-based reports
- Beautiful styling with charts and tables
- Can be opened in any web browser
- Perfect for sharing and viewing online
- Download button located in the top-right corner of the interface

**Download Options:**
- Use the download button in the web interface
- API endpoint: `/api/download/html`
- Reports include timestamps and comprehensive analysis data

## Usage

### Basic Usage

1. **Enter repository paths** (one per line):
   ```
   /path/to/repo1
   /path/to/repo2
   /path/to/repo3
   ```

2. **Select date range** for analysis

3. **Click "Analyze Repositories"** to start the analysis

4. **View results** in the dashboard

### Example Repository Paths

For your current project:
```
/Users/gauravvarshney/Downloads/Downloads/Projects/Car2.0/pbp.car.backend
/Users/gauravvarshney/Downloads/Downloads/Projects/Car2.0/pbp.car.frontend
```

## API Endpoints

### POST /api/analyze
Analyze multiple Git repositories.

**Request Body:**
```json
{
  "repoPaths": ["/path/to/repo1", "/path/to/repo2"],
  "startDate": "2025-01-01",
  "endDate": "2025-12-31"
}
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "name": "repo-name",
      "path": "/path/to/repo",
      "startDate": "2025-01-01",
      "endDate": "2025-12-31",
      "totalCommits": 150,
      "totalLinesAdded": 5000,
      "totalLinesRemoved": 1000,
      "developerStats": [
        {
          "name": "Developer Name",
          "commits": 25,
          "linesAdded": 1000,
          "linesRemoved": 200
        }
      ]
    }
  ]
}
```

### GET /api/health
Health check endpoint.

### POST /api/download/html
Generate and download HTML report.

## Features Explained

### Summary Cards
- **Repositories**: Total number of analyzed repositories
- **Total Commits**: Combined commits across all repositories
- **Lines Added**: Total lines of code added
- **Lines Removed**: Total lines of code removed

### Repository Analysis
- Individual repository statistics
- Developer contribution breakdown
- Interactive bar charts
- Detailed tables with commit counts

### Combined Statistics
- Aggregated developer data across all repositories
- Contribution percentages
- Net change calculations
- Sorted by productivity

## Technical Details

### Backend (Python/Flask)
- **server.py**: Main Flask application with dynamic configuration
- **config.py**: Dynamic configuration management system
- **Git integration**: Uses `git log` commands for analysis
- **CORS enabled**: Allows cross-origin requests
- **Error handling**: Graceful handling of invalid repositories

### Frontend (HTML/JavaScript)
- **Bootstrap 5**: Modern, responsive UI
- **Chart.js**: Interactive charts and visualizations
- **Vanilla JavaScript**: No framework dependencies
- **Async/await**: Modern JavaScript patterns

### Configuration System
- **Dynamic Configuration**: JSON-based configuration with runtime updates
- **Name Mappings**: Configurable developer name normalization
- **AI Keywords**: Customizable AI detection keywords and confidence levels
- **File Types**: Extensible code file extensions and exclude patterns
- **API Management**: RESTful endpoints for configuration management

### Git Commands Used
- `git log --since="date" --until="date" --format="%an" --numstat`
- Parses author names and line statistics
- Handles binary files and special cases

## Troubleshooting

### Common Issues

1. **"Repository path does not exist"**
   - Verify the repository path is correct
   - Ensure the path is absolute or relative to the server

2. **"Not a Git repository"**
   - Make sure the directory contains a `.git` folder
   - Check if Git is properly initialized

3. **"Git command failed"**
   - Ensure Git is installed and accessible
   - Check repository permissions

4. **"Error connecting to analysis server"**
   - Make sure the Python server is running
   - Check if port 5000 is available
   - Verify CORS settings

### Debug Mode

Run the server in debug mode for detailed error messages:
```bash
python server.py
```

## Customization

### Adding New Metrics
1. Modify `analyze_repository_git()` in `server.py`
2. Add new fields to the response JSON
3. Update the frontend to display new metrics

### Styling Changes
- Modify CSS in `index.html`
- Update Bootstrap classes for different themes
- Customize Chart.js options for different chart styles

### Date Format
The application uses ISO date format (YYYY-MM-DD). Modify the date parsing in `server.py` if needed.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the API documentation
3. Open an issue on the repository

---

**Happy analyzing with RepoPulse! 🚀** 