import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh


from datetime import datetime

st.set_page_config(page_title="Gold & Global Markets", layout="wide")
st.title("📊 Gold Price & Global Markets Analysis")
# สั่งให้ Refresh หน้าเว็บอัตโนมัติทุกๆ 60,000 มิลลิวินาที (1 นาที)
# key คือชื่ออะไรก็ได้เพื่อให้ระบบจำสถานะได้
count = st_autorefresh(interval=60000, limit=100, key="fizzbuzzcounter")


# 1. ฟังก์ชันดึงข้อมูล (ดึงมาทั้งยวงเพื่อใช้ทำ Candlestick และเปรียบเทียบตลาด)
@st.cache_data(ttl=60)
def get_all_market_data():
    tickers = ["GC=F", "^GSPC", "^N225", "THB=X"]
    # ดึงข้อมูล 5 วันย้อนหลัง รายชั่วโมง เพื่อให้เห็นความต่อเนื่องของตลาดเอเชียและอเมริกา
    raw_data = yf.download(tickers, period="5d", interval="1h", group_by='ticker')
    return raw_data

try:
    all_data = get_all_market_data()
    
    # ดึงเฉพาะข้อมูลทองคำออกมาใช้งานง่ายๆ
    gold_df = all_data['GC=F'].dropna()
    
    # --- ส่วนแสดงตัวเลข Metric ---
    current_gold_price = gold_df['Close'].iloc[-1]
    prev_gold_price = gold_df['Close'].iloc[-2]
    gold_delta = current_gold_price - prev_gold_price
    
    st.metric(label="Gold Price (USD/oz)", value=f"{current_gold_price:,.2f}", delta=f"{gold_delta:,.2f}")

    # --- ส่วนกราฟทองคำ ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Gold Line Chart (Trend)")
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(x=gold_df.index, y=gold_df['Close'], mode='lines', name='Price', line=dict(color='#FFD700')))
        fig_line.update_layout(height=400, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig_line, width="stretch")

    with col2:
        st.subheader("📊 Gold Candlestick (Analysis)")
        fig_candle = go.Figure(data=[go.Candlestick(    
            x=gold_df.index,
            open=gold_df['Open'],
            high=gold_df['High'],
            low=gold_df['Low'],
            close=gold_df['Close'],
            name='Market'
        )])
        fig_candle.update_layout(
            height=400, 
            margin=dict(l=0, r=0, t=0, b=0), 
            xaxis_rangeslider_visible=False,
            yaxis_title="Price (USD)",
            template="plotly_dark"  # เพิ่มเติม: ถ้าชอบธีมมืดให้ดูโปรขึ้น
        )
        st.plotly_chart(fig_candle, width="stretch", theme=None)

    st.divider() # เส้นคั่นแบ่งส่วน

    # --- ส่วนใหม่: กราฟตลาดอเมริกา vs เอเชีย ---
    st.subheader("🌎 Global Markets Comparison (US vs Asia)")
    
    col_us, col_asia = st.columns(2)

    with col_us:
        us_df = all_data['^GSPC'].dropna()
        st.write("🇺🇸 **US Market (S&P 500)**")
        fig_us = go.Figure()
        fig_us.add_trace(go.Scatter(x=us_df.index, y=us_df['Close'], name="S&P 500", line=dict(color='#00D1FF')))
        fig_us.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_us, width="stretch")

    with col_asia:
        asia_df = all_data['^N225'].dropna()
        st.write("🇯🇵 **Asia Market (Nikkei 225)**")
        fig_asia = go.Figure()
        fig_asia.add_trace(go.Scatter(x=asia_df.index, y=asia_df['Close'], name="Nikkei 225", line=dict(color='#FF4B4B')))
        fig_asia.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_asia, width="stretch")


        st.divider()

    # --- ส่วนใหม่: คำนวณราคาทองคำไทย ---
    st.subheader("🇹🇭 Thai Gold Price Estimation (ประมาณการราคาทองไทย)")
    
    # ดึงค่าเงินบาทล่าสุด
    thb_df = all_data['THB=X'].dropna()
    current_thb = thb_df['Close'].iloc[-1]
    
    # คำนวณราคาทองไทย (สูตร: Spot * 0.4729 * USDTHB)
    # 0.4729 คือ ค่าคงที่แปลง Oz เป็น บาททอง (96.5%)
    thai_gold_estimate = (current_gold_price * 0.4729 * current_thb)
    
    col_calc1, col_calc2, col_calc3 = st.columns(3)
    
    with col_calc1:
        st.metric(label="ค่าเงินบาท (USD/THB)", value=f"{current_thb:.2f} บาท")
        
    with col_calc2:
        st.info(f"**สูตรคำนวณ:** ({current_gold_price:,.2f} × 0.4729 × {current_thb:.2f})")
        
    with col_calc3:
        # แสดงราคาทองไทยโดยประมาณ
        st.success(f"**ราคาประมาณการ:** {thai_gold_estimate:,.0f} บาท")
        st.caption("*เป็นราคาคำนวณเบื้องต้น ยังไม่รวมค่าพรีเมียมและส่วนต่างสมาคม")


except Exception as e:
    st.error(f"เกิดข้อผิดพลาด: {e}")