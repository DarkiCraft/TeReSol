import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns

# Page configuration
st.set_page_config(
    layout="wide", 
    page_title="NASDAQ Dashboard",
    page_icon="📈"
)

# Custom CSS for modern dashboard styling
st.markdown("""
<style>
    /* Hide default streamlit styling */
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    .stApp > header {visibility: hidden;}
    
    /* Main container styling */

    
    /* Navigation bar styling */
    .nav-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1rem 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
        border: 1px solid rgba(255, 255, 255, 0.18);
    }
    
    /* Card styling */
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
        border: 1px solid rgba(255, 255, 255, 0.18);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    /* Content card styling */
    
    /* Section header styling */
    .section-header {
        color: #2c3e50;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-align: center;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Stock icon styling */
    .stock-icon {
        font-size: 3rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    /* Navigation buttons */
    .nav-button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 10px;
        font-weight: 600;
        margin: 0 0.5rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .nav-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    .nav-button.active {
        background: linear-gradient(45deg, #764ba2, #667eea);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.6);
    }
    
    /* Dropdown styling */
    .stSelectbox > div > div {
        border-radius: 10px;
        border: 2px solid #e1e5e9;
        background: rgba(255, 255, 255, 0.9);
    }
    
    /* Upload area styling */
    .uploadedfile {
        border-radius: 15px;
        border: 2px dashed #667eea;
        padding: 2rem;
        text-align: center;
        background: rgba(102, 126, 234, 0.1);
    }
</style>
""", unsafe_allow_html=True)

API_BASE = "http://localhost:8000"

# --- Cached API Calls ---
@st.cache_data
def get_all_stocks():
    return pd.DataFrame(requests.get(f"{API_BASE}/stocks").json())

@st.cache_data
def get_etf_dist():
    return requests.get(f"{API_BASE}/distribution/etf").json()

@st.cache_data
def get_categories_dist():
    return requests.get(f"{API_BASE}/distribution/categories").json()

@st.cache_data
def get_stock_metadata(symbol):
    return requests.get(f"{API_BASE}/stocks/{symbol}").json()

@st.cache_data
def get_stock_price_data(symbol):
    df = pd.DataFrame(requests.get(f"{API_BASE}/stocks/{symbol}/data").json())
    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)
    return df.sort_index()

# Initialize session state for navigation
if 'active_section' not in st.session_state:
    st.session_state.active_section = 'Overview'

# Navigation header
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Title and navigation
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div class="nav-container">
        <div style="text-align: center;">
            <h1 style="color: #2c3e50; margin-bottom: 1rem;">📈 Stock Exchange Analytics Dashboard</h1>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Navigation buttons
nav_col1, nav_col2, nav_col3, nav_col4, nav_col5, nav_col6 = st.columns(6)

with nav_col1:
    if st.button("📊 Overview", key="nav_overview", use_container_width=True):
        st.session_state.active_section = 'Overview'

with nav_col2:
    if st.button("📈 Market Analysis", key="nav_market", use_container_width=True):
        st.session_state.active_section = 'Market Analysis'

with nav_col3:
    if st.button("🔍 Advanced Analytics", key="nav_advanced", use_container_width=True):
        st.session_state.active_section = 'Advanced Analytics'

with nav_col4:
    if st.button("💹 Stock Data", key="nav_stock_data", use_container_width=True):
        st.session_state.active_section = 'Stock Data'

with nav_col5:
    if st.button("📉 Visualizations", key="nav_viz", use_container_width=True):
        st.session_state.active_section = 'Visualizations'

with nav_col6:
    if st.button("📁 File Upload", key="nav_upload", use_container_width=True):
        st.session_state.active_section = 'File Upload'

st.markdown("<br>", unsafe_allow_html=True)

# --- OVERVIEW SECTION ---
if st.session_state.active_section == 'Overview':
    st.markdown('<h2 class="section-header">Market Overview</h2>', unsafe_allow_html=True)
    
    df = get_all_stocks()
    etf_data = get_etf_dist()
    
    # Metrics cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="stock-icon">🏢</div>
            <h3 style="text-align: center; color: #2c3e50;">Total Stocks</h3>
            <h1 style="text-align: center; color: #667eea;">{}</h1>
        </div>
        """.format(df["Symbol"].nunique()), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="stock-icon">🏦</div>
            <h3 style="text-align: center; color: #2c3e50;">Exchanges</h3>
            <h1 style="text-align: center; color: #667eea;">{}</h1>
        </div>
        """.format(df["Listing Exchange"].nunique()), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="stock-icon">📊</div>
            <h3 style="text-align: center; color: #2c3e50;">ETFs</h3>
            <h1 style="text-align: center; color: #667eea;">{}</h1>
        </div>
        """.format(etf_data.get("Y", 0)), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="stock-icon">📈</div>
            <h3 style="text-align: center; color: #2c3e50;">Non-ETFs</h3>
            <h1 style="text-align: center; color: #667eea;">{}</h1>
        </div>
        """.format(etf_data.get("N", 0)), unsafe_allow_html=True)
    
    # Exchange distribution table
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown("### 🏛️ Exchange Distribution")
    exchange_counts = df["Listing Exchange"].value_counts()
    
    # Create fancy exchange distribution with progress bars and styling
    total_stocks = exchange_counts.sum()
    
    for i, (exchange, count) in enumerate(exchange_counts.items()):
        percentage = (count / total_stocks) * 100
        
        # Color gradient for different exchanges
        colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe']
        color = colors[i % len(colors)]
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(90deg, {color}20 0%, {color}10 {percentage}%, transparent {percentage}%);
            border-left: 4px solid {color};
            padding: 15px;
            margin: 10px 0;
            border-radius: 10px;
            backdrop-filter: blur(5px);
            transition: transform 0.3s ease;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h4 style="margin: 0; color: #2c3e50; font-weight: 600;">{exchange}</h4>
                    <p style="margin: 0; color: #7f8c8d; font-size: 0.9em;">Market Exchange</p>
                </div>
                <div style="text-align: right;">
                    <h3 style="margin: 0; color: {color}; font-weight: 700;">{count:,}</h3>
                    <p style="margin: 0; color: #7f8c8d; font-size: 0.8em;">{percentage:.1f}% of total</p>
                </div>
            </div>
            <div style="
                width: 100%; 
                height: 6px; 
                background: rgba(0,0,0,0.1); 
                border-radius: 3px; 
                margin-top: 10px;
                overflow: hidden;
            ">
                <div style="
                    width: {percentage}%; 
                    height: 100%; 
                    background: linear-gradient(90deg, {color}, {color}dd);
                    border-radius: 3px;
                    transition: width 0.8s ease;
                "></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- MARKET ANALYSIS SECTION ---
elif st.session_state.active_section == 'Market Analysis':
    st.markdown('<h2 class="section-header">Market Analysis & Visualizations</h2>', unsafe_allow_html=True)
    
    df = get_all_stocks()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Stocks per Exchange")
        fig = px.bar(
            x=df["Listing Exchange"].value_counts().index,
            y=df["Listing Exchange"].value_counts().values,
            color=df["Listing Exchange"].value_counts().values,
            color_continuous_scale="Viridis"
        )
        fig.update_layout(  
            xaxis_title="Listing Exchange",
            yaxis_title="Number of Stocks",
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🥧 Market Categories")
        cat = get_categories_dist()
        
        descriptive_categories = {}
        for key, value in cat.items():
            if key == 'Q':
                descriptive_categories['Global Select Market'] = value
            elif key == 'G':
                descriptive_categories['Global Market'] = value
            elif key == 'S':
                descriptive_categories['Capital Market'] = value
            elif key == 'Missing':
                descriptive_categories['Missing Data'] = value
            else:
                descriptive_categories[key] = value
        
        fig = px.pie(
            names=list(descriptive_categories.keys()),
            values=list(descriptive_categories.values()),
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- ADVANCED ANALYTICS SECTION ---
elif st.session_state.active_section == 'Advanced Analytics':
    st.markdown('<h2 class="section-header">Advanced Market Analytics</h2>', unsafe_allow_html=True)
    
    df_meta = get_all_stocks()
    etf = get_etf_dist()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔄 ETF Distribution")
        fig = px.pie(
            names=["ETFs", "Non-ETFs"],
            values=[etf.get("Y", 0), etf.get("N", 0)],
            color_discrete_sequence=['#667eea', '#764ba2']
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📦 Top Companies by Round Lot Size")
        if "Round Lot Size" in df_meta.columns:
            df_meta["Round Lot Size"] = pd.to_numeric(df_meta["Round Lot Size"], errors="coerce")
            top10 = df_meta.sort_values("Round Lot Size", ascending=False).head(10)
            st.dataframe(top10[["Symbol", "Security Name", "Round Lot Size"]], use_container_width=True)
        else:
            st.warning("Round Lot Size column not found in metadata.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Scatter plot and correlation matrix
    if "Round Lot Size" in df_meta.columns:
        st.markdown("### 📈 Round Lot Size Analysis")
        df_meta["Round Lot Size"] = pd.to_numeric(df_meta["Round Lot Size"], errors="coerce")
        top10 = df_meta.sort_values("Round Lot Size", ascending=False).head(10)
        fig_scatter = px.scatter(
            top10, 
            x="Symbol", 
            y="Round Lot Size", 
            size="Round Lot Size", 
            color="Symbol",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_scatter.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Correlation matrix
    st.markdown("### 🔗 Correlation Matrix")
    num_df = df_meta.select_dtypes(include=["float64", "int64"]).dropna(axis=1, how="any")
    
    if not num_df.empty:
        corr = num_df.corr()
        fig_corr, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(corr, annot=True, cmap="RdYlBu_r", ax=ax, center=0)
        ax.set_title("Correlation Matrix", fontsize=16, fontweight='bold')
        st.pyplot(fig_corr)
    else:
        st.info("No numeric columns found for correlation matrix.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- STOCK DATA SECTION ---
elif st.session_state.active_section == 'Stock Data':
    st.markdown('<h2 class="section-header">Individual Stock Analysis</h2>', unsafe_allow_html=True)
    
    df = get_all_stocks()
    
    col1, col2 = st.columns([1, 1])
    with col1:
        symbol = st.selectbox(
            "🔍 Select Stock Symbol", 
            df["Symbol"].sort_values(), 
            key="stock_data_select"
        )
    
    with col2:
        analysis_type = st.selectbox(
            "📊 Analysis Type",
            ["Summary Statistics", "Daily Returns"],
            key="analysis_type_select"
        )
    
    if symbol:
        data = get_stock_price_data(symbol)
        meta = get_stock_metadata(symbol)
        
        # Metadata card
        st.markdown(f"### 💼 {symbol} - Company Information")
        meta_df = pd.DataFrame([meta])
        st.dataframe(meta_df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Analysis content
        if analysis_type == "Summary Statistics":
            st.markdown(f"### 📈 {symbol} - Summary Statistics")
            st.dataframe(data.describe(), use_container_width=True)
        
        elif analysis_type == "Daily Returns":
            st.markdown(f"### 📊 {symbol} - Daily Returns")
            data["Daily Return"] = data["Close"].pct_change()
            df_returns = data["Daily Return"].dropna().reset_index()
            df_returns.columns = ["Date", "Daily Return"]
            fig = px.line(
                df_returns, 
                x="Date", 
                y="Daily Return",
                line_shape="spline"
            )
            fig.update_traces(line_color='#667eea')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="",
                yaxis_title="Daily Return"
            )
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- VISUALIZATIONS SECTION ---
elif st.session_state.active_section == 'Visualizations':
    st.markdown('<h2 class="section-header">Stock Visualizations</h2>', unsafe_allow_html=True)
    
    df = get_all_stocks()
    
    col1, col2 = st.columns([1, 1])
    with col1:
        symbol = st.selectbox(
            "🔍 Select Stock for Visualization", 
            df["Symbol"].sort_values(), 
            key="viz_stock_select"
        )
    
    with col2:
        viz_type = st.selectbox(
            "📈 Visualization Type",
            ["Price Over Time", "Moving Averages", "Volatility"],
            key="viz_type_select"
        )
    
    if symbol:
        data = get_stock_price_data(symbol)
        meta = get_stock_metadata(symbol)
        
        # Metadata card
        st.markdown(f"### 💼 {symbol} - Company Information")
        meta_df = pd.DataFrame([meta])
        st.dataframe(meta_df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Visualization content
        if viz_type == "Price Over Time":
            st.markdown(f"### 📈 {symbol} - Price Over Time")
            df_price = data["Close"].dropna().reset_index()
            df_price.columns = ["Date", "Close"]
            fig = px.line(
                df_price, 
                x="Date", 
                y="Close",
                line_shape="spline"
            )
            fig.update_traces(line_color='#667eea', line_width=3)
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="",
                yaxis_title="Close Price ($)"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        elif viz_type == "Moving Averages":
            st.markdown(f"### 📊 {symbol} - Moving Averages")
            data["SMA20"] = data["Close"].rolling(20).mean()
            data["SMA50"] = data["Close"].rolling(50).mean()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=data.index, y=data["Close"], name="Close", line=dict(color='#667eea', width=2)))
            fig.add_trace(go.Scatter(x=data.index, y=data["SMA20"], name="SMA 20", line=dict(color='#764ba2', width=2)))
            fig.add_trace(go.Scatter(x=data.index, y=data["SMA50"], name="SMA 50", line=dict(color='#f093fb', width=2)))
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="",
                yaxis_title="Price ($)"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        elif viz_type == "Volatility":
            st.markdown(f"### 📉 {symbol} - Volatility (20-day Rolling Std)")
            data["Volatility"] = data["Close"].pct_change().rolling(20).std()
            fig = px.line(data.reset_index(), x="Date", y="Volatility")
            fig.update_traces(line_color='#ff6b6b', line_width=3)
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="",
                yaxis_title="Volatility"
            )
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- FILE UPLOAD SECTION ---
elif st.session_state.active_section == 'File Upload':
    st.markdown('<h2 class="section-header">File Upload & Analysis</h2>', unsafe_allow_html=True)
    
    st.markdown("### 📁 Upload Stock Data File")
    
    uploaded_file = st.file_uploader(
        "Choose a CSV or TXT file", 
        type=["csv", "txt"],
        help="Upload your stock data file for analysis"
    )
    
    if uploaded_file is not None:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        if st.button("🚀 Analyze File", use_container_width=True):
            files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
            try:
                response = requests.post("http://localhost:8000/upload", files=files)
                json_data = response.json()

                meta = json_data["metadata"]
                processed_data = pd.DataFrame(json_data["data"])
                processed_data["Date"] = pd.to_datetime(processed_data["Date"])
                processed_data.set_index("Date", inplace=True)
                processed_data = processed_data.sort_index()
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Metadata
                st.markdown("### 💼 File Metadata")
                st.dataframe(pd.DataFrame([meta]), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Analysis tabs
                tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Summary", "📈 Returns", "💹 Price", "📉 Moving Avg", "⚡ Volatility"])
                
                with tab1:
                    st.markdown("### 📊 Summary Statistics")
                    st.dataframe(processed_data.describe(), use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with tab2:
                    st.markdown("### 📈 Daily Returns")
                    daily_returns_df = processed_data["Close"].pct_change().dropna().reset_index()
                    daily_returns_df.columns = ["Date", "Daily Return"]
                    fig = px.line(daily_returns_df, x="Date", y="Daily Return")
                    fig.update_traces(line_color='#667eea')
                    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with tab3:
                    st.markdown("### 💹 Price Over Time")
                    price_df = processed_data["Close"].dropna().reset_index()
                    price_df.columns = ["Date", "Close"]
                    fig = px.line(price_df, x="Date", y="Close")
                    fig.update_traces(line_color='#764ba2')
                    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with tab4:
                    st.markdown("### 📉 Moving Averages")
                    processed_data["SMA20"] = processed_data["Close"].rolling(20).mean()
                    processed_data["SMA50"] = processed_data["Close"].rolling(50).mean()
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=processed_data.index, y=processed_data["Close"], name="Close", line=dict(color='#667eea')))
                    fig.add_trace(go.Scatter(x=processed_data.index, y=processed_data["SMA20"], name="SMA 20", line=dict(color='#764ba2')))
                    fig.add_trace(go.Scatter(x=processed_data.index, y=processed_data["SMA50"], name="SMA 50", line=dict(color='#f093fb')))
                    
                    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with tab5:
                    st.markdown("### ⚡ Volatility Analysis")
                    processed_data["Volatility"] = processed_data["Close"].pct_change().rolling(20).std()
                    fig = px.line(processed_data.reset_index(), x="Date", y="Volatility")
                    fig.update_traces(line_color='#ff6b6b')
                    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ Upload failed: {str(e)}")
    else:
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)