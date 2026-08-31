import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 頁面基本設定
st.set_page_config(
    page_title="美國宏觀經濟儀表板",
    page_icon="📈",
    layout="wide"
)

# 標題與簡介
st.title("🇺🇸 美國宏觀經濟與市場指標儀表板")
st.markdown("即時追蹤美股大盤、美債殖利率、美元指數與重要商品走勢（免 API Key）")

# 側邊欄設定
st.sidebar.header("📊 設定選項")
period = st.sidebar.selectbox(
    "選擇時間範圍", 
    ["1mo", "3mo", "6mo", "1y", "2y", "5y"], 
    index=3,
    format_func=lambda x: {
        "1mo": "近 1 個月",
        "3mo": "近 3 個月",
        "6mo": "近 6 個月",
        "1y": "近 1 年",
        "2y": "近 2 年",
        "5y": "近 5 年"
    }[x]
)

if st.sidebar.button("🔄 立即更新數據"):
    st.cache_data.clear()
    st.rerun()

# 設定追蹤的指標與 yfinance 代碼
tickers = {
    "S&P 500 指數": "^GSPC",
    "納斯達克 100 指數": "^NDX",
    "美國 10 年期國債殖利率": "^TNX",
    "美元指數 (DXY)": "DX-Y.NY",
    "黃金期貨": "GC=F",
    "紐約原油期貨": "CL=F"
}

@st.cache_data(ttl=300)  # 快取縮短為 5 分鐘
def load_data(symbol, time_period):
    try:
        data = yf.Ticker(symbol).history(period=time_period)
        return data
    except Exception:
        return pd.DataFrame()

# 數據指標區塊
st.subheader("📌 重要指標實時概覽")

cols = st.columns(3)
idx = 0

for name, symbol in tickers.items():
    df = load_data(symbol, period)
    if not df.empty and len(df) > 1:
        latest_price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2]
        change = latest_price - prev_price
        pct_change = (change / prev_price) * 100
        
        with cols[idx % 3]:
            st.metric(
                label=name,
                value=f"{latest_price:,.2f}",
                delta=f"{change:+,.2f} ({pct_change:+.2f}%)"
            )
        idx += 1

st.divider()

# 圖表展示區塊
st.subheader("📈 歷史走勢折線圖")

selected_ticker = st.selectbox("選擇要放大檢視的指標", list(tickers.keys()))
selected_symbol = tickers[selected_ticker]

chart_df = load_data(selected_symbol, period)

if not chart_df.empty:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=chart_df.index, 
        y=chart_df['Close'], 
        mode='lines', 
        name=selected_ticker,
        line=dict(color='#0066cc', width=2)
    ))
    fig.update_layout(
        title=f"{selected_ticker} 歷史趨勢圖",
        xaxis_title="日期",
        yaxis_title="價格 / 指數",
        template="plotly_white",
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("無法取得資料，請稍後重試。")
