"""
Streamlit Dashboard for Data Redaction Gateway Metrics.

This dashboard visualizes:
- Real-time gateway performance metrics
- LLM Judge evaluation results
- Redaction quality trends
- Request success/failure rates
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from typing import Dict, Any, List
import time

# Page configuration
st.set_page_config(
    page_title="Redaction Gateway Metrics",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
API_BASE_URL = st.sidebar.text_input(
    "API Base URL",
    value="http://127.0.0.1:8000",
    help="Base URL of the Data Redaction Gateway API"
)

# Styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .success-metric {
        color: #28a745;
        font-weight: bold;
    }
    .error-metric {
        color: #dc3545;
        font-weight: bold;
    }
    .warning-metric {
        color: #ffc107;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# Helper functions
@st.cache_data(ttl=30)  # Cache for 30 seconds
def fetch_aggregated_metrics(start_time: datetime, end_time: datetime, period: str = "hour") -> Dict[str, Any]:
    """Fetch aggregated metrics from API."""
    try:
        url = f"{API_BASE_URL}/metrics/db/aggregated"
        params = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "period": period
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching aggregated metrics: {e}")
        return None


@st.cache_data(ttl=30)
def fetch_time_series(start_time: datetime, end_time: datetime, interval_minutes: int = 5) -> List[Dict[str, Any]]:
    """Fetch time-series metrics from API."""
    try:
        url = f"{API_BASE_URL}/metrics/db/timeseries"
        params = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "interval_minutes": interval_minutes
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching time-series metrics: {e}")
        return []


@st.cache_data(ttl=30)
def fetch_redaction_quality(start_time: datetime, end_time: datetime) -> Dict[str, Any]:
    """Fetch redaction quality summary from API."""
    try:
        url = f"{API_BASE_URL}/metrics/db/redaction-quality"
        params = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching redaction quality: {e}")
        return None


def check_api_health() -> bool:
    """Check if metrics API is healthy."""
    try:
        url = f"{API_BASE_URL}/metrics/db/health"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get("status") == "healthy"
    except:
        return False


# Main dashboard
def main():
    # Header
    st.markdown('<div class="main-header">🔒 Data Redaction Gateway Metrics</div>', unsafe_allow_html=True)
    
    # Sidebar - Time range selection
    st.sidebar.markdown("## ⏰ Time Range")
    time_range = st.sidebar.selectbox(
        "Select Time Range",
        ["Last 15 minutes", "Last 1 hour", "Last 6 hours", "Last 24 hours", "Last 7 days", "Custom"],
        index=1
    )
    
    # Calculate time range
    end_time = datetime.utcnow()
    if time_range == "Last 15 minutes":
        start_time = end_time - timedelta(minutes=15)
        interval_minutes = 1
    elif time_range == "Last 1 hour":
        start_time = end_time - timedelta(hours=1)
        interval_minutes = 5
    elif time_range == "Last 6 hours":
        start_time = end_time - timedelta(hours=6)
        interval_minutes = 15
    elif time_range == "Last 24 hours":
        start_time = end_time - timedelta(hours=24)
        interval_minutes = 30
    elif time_range == "Last 7 days":
        start_time = end_time - timedelta(days=7)
        interval_minutes = 360  # 6 hours
    else:  # Custom
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=end_time.date() - timedelta(days=1))
            start_time_input = st.time_input("Start Time", value=datetime.min.time())
        with col2:
            end_date = st.date_input("End Date", value=end_time.date())
            end_time_input = st.time_input("End Time", value=end_time.time())
        
        start_time = datetime.combine(start_date, start_time_input)
        end_time = datetime.combine(end_date, end_time_input)
        interval_minutes = st.sidebar.slider("Interval (minutes)", 1, 60, 5)
    
    # Auto-refresh
    auto_refresh = st.sidebar.checkbox("Auto-refresh", value=True)
    if auto_refresh:
        refresh_interval = st.sidebar.slider("Refresh interval (seconds)", 10, 300, 30)
        st.sidebar.info(f"Dashboard will refresh every {refresh_interval} seconds")
    
    # API Health Check
    api_healthy = check_api_health()
    if api_healthy:
        st.sidebar.success("✅ API Connected")
    else:
        st.sidebar.error("❌ API Disconnected")
        st.error("Cannot connect to the metrics API. Please check the API Base URL and ensure the server is running.")
        return
    
    # Fetch data
    with st.spinner("Loading metrics..."):
        aggregated = fetch_aggregated_metrics(start_time, end_time)
        time_series = fetch_time_series(start_time, end_time, interval_minutes)
        quality_data = fetch_redaction_quality(start_time, end_time)
    
    if not aggregated:
        st.warning("No metrics data available for the selected time range.")
        return
    
    # KPI Cards
    st.markdown("## 📊 Key Performance Indicators")
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)
    
    with kpi_col1:
        st.metric(
            "Total Requests",
            f"{aggregated['total_requests']:,}",
            help="Total number of requests received"
        )
    
    with kpi_col2:
        success_rate = aggregated['success_rate']
        st.metric(
            "Success Rate",
            f"{success_rate:.1f}%",
            delta=f"{aggregated['successful_requests']} successful",
            delta_color="normal" if success_rate >= 95 else "inverse"
        )
    
    with kpi_col3:
        st.metric(
            "Failed Requests",
            f"{aggregated['failed_requests']:,}",
            delta=f"{aggregated['error_rate']:.1f}% error rate",
            delta_color="inverse" if aggregated['error_rate'] > 5 else "off"
        )
    
    with kpi_col4:
        st.metric(
            "LLM Judge Calls",
            f"{aggregated['llm_calls']:,}",
            help="Number of LLM judge evaluations"
        )
    
    with kpi_col5:
        st.metric(
            "Avg Latency",
            f"{aggregated['avg_latency_ms']:.1f}ms",
            delta=f"P95: {aggregated['p95_latency_ms']:.1f}ms",
            delta_color="off"
        )
    
    # Time Series Charts
    st.markdown("---")
    st.markdown("## 📈 Request Trends Over Time")
    
    if time_series:
        df_ts = pd.DataFrame(time_series)
        df_ts['timestamp'] = pd.to_datetime(df_ts['timestamp'])
        
        # Requests over time
        fig_requests = go.Figure()
        fig_requests.add_trace(go.Scatter(
            x=df_ts['timestamp'],
            y=df_ts['total_requests'],
            mode='lines+markers',
            name='Total Requests',
            line=dict(color='#1f77b4', width=2),
            fill='tozeroy'
        ))
        fig_requests.add_trace(go.Scatter(
            x=df_ts['timestamp'],
            y=df_ts['successful_requests'],
            mode='lines+markers',
            name='Successful',
            line=dict(color='#28a745', width=2)
        ))
        fig_requests.add_trace(go.Scatter(
            x=df_ts['timestamp'],
            y=df_ts['failed_requests'],
            mode='lines+markers',
            name='Failed',
            line=dict(color='#dc3545', width=2)
        ))
        fig_requests.update_layout(
            title="Requests Over Time",
            xaxis_title="Time",
            yaxis_title="Number of Requests",
            hovermode='x unified',
            height=400
        )
        st.plotly_chart(fig_requests, use_container_width=True)
        
        # LLM Judge calls over time
        fig_llm = go.Figure()
        fig_llm.add_trace(go.Scatter(
            x=df_ts['timestamp'],
            y=df_ts['llm_calls'],
            mode='lines+markers',
            name='LLM Judge Calls',
            line=dict(color='#ff7f0e', width=2),
            fill='tozeroy'
        ))
        fig_llm.update_layout(
            title="LLM Judge Invocations Over Time",
            xaxis_title="Time",
            yaxis_title="Number of LLM Calls",
            hovermode='x unified',
            height=300
        )
        st.plotly_chart(fig_llm, use_container_width=True)
    else:
        st.info("No time-series data available for the selected range.")
    
    # Redaction Quality Analysis
    st.markdown("---")
    st.markdown("## 🎯 Redaction Quality Analysis")
    
    if quality_data and quality_data['total_evaluated'] > 0:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Quality summary metrics
            st.markdown("### Summary")
            st.metric("Total Evaluated", f"{quality_data['total_evaluated']:,}")
            st.metric("Good Redactions", f"{quality_data['good']:,}", 
                     delta=f"{quality_data['good_percentage']:.1f}%", 
                     delta_color="normal")
            st.metric("Under-Redacted", f"{quality_data['under_redacted']:,}",
                     delta=f"{quality_data['under_redacted_percentage']:.1f}%",
                     delta_color="inverse")
            st.metric("Over-Redacted", f"{quality_data['over_redacted']:,}",
                     delta=f"{quality_data['over_redacted_percentage']:.1f}%",
                     delta_color="inverse")
        
        with col2:
            # Pie chart
            quality_labels = ['Good', 'Under-Redacted', 'Over-Redacted']
            quality_values = [
                quality_data['good'],
                quality_data['under_redacted'],
                quality_data['over_redacted']
            ]
            quality_colors = ['#28a745', '#ffc107', '#dc3545']
            
            fig_quality = go.Figure(data=[go.Pie(
                labels=quality_labels,
                values=quality_values,
                marker=dict(colors=quality_colors),
                hole=0.4,
                textinfo='label+percent',
                textposition='outside'
            )])
            fig_quality.update_layout(
                title="Redaction Quality Distribution",
                height=400,
                showlegend=True
            )
            st.plotly_chart(fig_quality, use_container_width=True)
            
            # Bar chart
            fig_bar = px.bar(
                x=quality_labels,
                y=quality_values,
                color=quality_labels,
                color_discrete_map={
                    'Good': '#28a745',
                    'Under-Redacted': '#ffc107',
                    'Over-Redacted': '#dc3545'
                },
                title="Redaction Quality Counts",
                labels={'x': 'Quality Category', 'y': 'Count'}
            )
            fig_bar.update_layout(showlegend=False, height=300)
            st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No LLM judge evaluations available for the selected time range.")
    
    # Additional Metrics
    st.markdown("---")
    st.markdown("## 📋 Additional Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Performance")
        st.metric("Total Redactions", f"{aggregated['total_redactions']:,}")
        st.metric("P95 Latency", f"{aggregated['p95_latency_ms']:.2f}ms")
        st.metric("P99 Latency", f"{aggregated['p99_latency_ms']:.2f}ms")
    
    with col2:
        st.markdown("### Cache Efficiency")
        cache_rate = aggregated['cache_hit_rate']
        st.metric(
            "Cache Hit Rate",
            f"{cache_rate:.1f}%",
            delta_color="normal" if cache_rate >= 70 else "inverse"
        )
    
    with col3:
        st.markdown("### Quality Score")
        if quality_data and quality_data['total_evaluated'] > 0:
            quality_score = quality_data['good_percentage']
            st.metric(
                "Quality Score",
                f"{quality_score:.1f}%",
                help="Percentage of good redactions",
                delta_color="normal" if quality_score >= 90 else "inverse"
            )
        else:
            st.info("No quality data available")
    
    # Redaction Quality Trend (if time series has quality data)
    if time_series:
        st.markdown("---")
        st.markdown("## 🔍 Redaction Quality Trend")
        
        df_quality_trend = pd.DataFrame(time_series)
        df_quality_trend['timestamp'] = pd.to_datetime(df_quality_trend['timestamp'])
        
        fig_quality_trend = go.Figure()
        fig_quality_trend.add_trace(go.Scatter(
            x=df_quality_trend['timestamp'],
            y=df_quality_trend['good_redaction'],
            mode='lines+markers',
            name='Good',
            line=dict(color='#28a745', width=2),
            stackgroup='one'
        ))
        fig_quality_trend.add_trace(go.Scatter(
            x=df_quality_trend['timestamp'],
            y=df_quality_trend['under_redacted'],
            mode='lines+markers',
            name='Under-Redacted',
            line=dict(color='#ffc107', width=2),
            stackgroup='one'
        ))
        fig_quality_trend.add_trace(go.Scatter(
            x=df_quality_trend['timestamp'],
            y=df_quality_trend['over_redacted'],
            mode='lines+markers',
            name='Over-Redacted',
            line=dict(color='#dc3545', width=2),
            stackgroup='one'
        ))
        fig_quality_trend.update_layout(
            title="Redaction Quality Trend",
            xaxis_title="Time",
            yaxis_title="Count",
            hovermode='x unified',
            height=400
        )
        st.plotly_chart(fig_quality_trend, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown(f"*Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC*")
    
    # Auto-refresh
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()


if __name__ == "__main__":
    main()
