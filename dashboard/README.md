# Data Redaction Gateway - Metrics Dashboard

## Overview
This Streamlit dashboard provides real-time visualization of Data Redaction Gateway metrics, including:
- Request success/failure rates
- LLM Judge evaluation results
- Redaction quality analysis
- Performance metrics and trends

## Features
- **Real-time KPIs**: Total requests, success rate, LLM calls, latency
- **Time-series charts**: Request trends over customizable time ranges
- **Redaction quality analysis**: Pie charts and bar charts showing under/over-redaction counts
- **Auto-refresh**: Configurable auto-refresh for live monitoring
- **Flexible time ranges**: From 15 minutes to 7 days, or custom range

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Ensure API is Running
Make sure the Data Redaction Gateway API is running and accessible. Default URL: `http://127.0.0.1:8000`

## Running the Dashboard

### Start the Streamlit App
```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`

### Quick Start Script (Windows)
```powershell
.\run_dashboard.ps1
```

## Configuration

### API Base URL
- Default: `http://127.0.0.1:8000`
- Can be changed in the sidebar of the dashboard

### Auto-Refresh
- Enable/disable in the sidebar
- Adjustable refresh interval (10-300 seconds)

### Time Ranges
Choose from:
- Last 15 minutes
- Last 1 hour (default)
- Last 6 hours
- Last 24 hours
- Last 7 days
- Custom range

## Dashboard Sections

### 1. Key Performance Indicators (KPIs)
Displays at-a-glance metrics:
- Total Requests
- Success Rate
- Failed Requests
- LLM Judge Calls
- Average Latency

### 2. Request Trends Over Time
Time-series line charts showing:
- Total, successful, and failed requests
- LLM judge invocations

### 3. Redaction Quality Analysis
Visual analysis of LLM judge evaluations:
- Summary metrics (good/under-redacted/over-redacted)
- Pie chart showing distribution
- Bar chart with counts
- Quality trend over time

### 4. Additional Metrics
- Performance metrics (P95, P99 latency)
- Cache hit rate
- Quality score percentage

## API Endpoints Used

The dashboard connects to these metrics API endpoints:

- `GET /metrics/aggregated` - Aggregated metrics for time range
- `GET /metrics/timeseries` - Time-series data points
- `GET /metrics/redaction-quality` - Redaction quality summary
- `GET /metrics/health` - API health check

## Troubleshooting

### Dashboard shows "API Disconnected"
- Verify the API is running: `http://127.0.0.1:8000/docs`
- Check the API Base URL in the sidebar
- Ensure no firewall is blocking the connection

### No data displayed
- Verify requests are being logged to the metrics database
- Check the selected time range includes periods with traffic
- Review API logs for errors

### Slow performance
- Reduce the time range or increase the interval
- Disable auto-refresh for large datasets
- Consider implementing metrics aggregation

## Data Storage

Metrics are stored in an SQLite database at:
```
<project_root>/data/metrics.db
```

The database contains:
- Individual request metrics
- LLM judge evaluation results
- Redaction quality assessments

## Development

### Adding New Visualizations
1. Create a new section in `app.py`
2. Fetch required data using the API helper functions
3. Use Plotly for interactive charts

### Customizing Appearance
- Modify the CSS in the `st.markdown()` style section
- Adjust Plotly chart layouts and colors
- Configure Streamlit theme in `.streamlit/config.toml`

## Production Deployment

For production use:
- Use a production-grade database (PostgreSQL)
- Implement authentication
- Deploy with Docker or cloud services
- Set up monitoring and alerting

## Support

For issues or questions:
- Check the main project README
- Review API documentation at `/docs`
- Check application logs
