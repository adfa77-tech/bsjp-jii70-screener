import streamlit as st
import pandas as pd
import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Konfigurasi Halaman Streamlit (Wide mode)
st.set_page_config(
    page_title="BSJP JII70 Pro Screener & Calculator",
    page_icon="📈",
    layout="wide"
)

# Custom CSS untuk merapikan dan mengecilkan padding agar compact
st.markdown("""
    <style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
    }
    .stMetric {
        background: rgba(22, 27, 34, 0.7);
        padding: 10px;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# Cek & Import yfinance secara aman
try:
    import yfinance as yf
except ImportError:
    st.error("Library `yfinance` belum terinstal. Silakan jalankan `pip install yfinance` di terminal Anda.")
    st.stop()

# --- FUNGSI AMBIL DATA IHSG & PASAR ---
@st.cache_data(ttl=600)
def get_ihsg_data():
    try:
        ihsg = yf.Ticker("^JKSE").history(period="5d")
        if not ihsg.empty:
            latest = ihsg.iloc[-1]
            prev = ihsg.iloc[-2]
            change = ((latest['Close'] - prev['Close']) / prev['Close']) * 100
            return float(latest['Close']), float(change)
    except Exception:
        pass
    return 7200.0, 0.0

ihsg_price, ihsg_change = get_ihsg_data()

# Header Ticker IHSG Compact
st.markdown(f"""
    <div style="background: rgba(22, 27, 34, 0.8); padding: 8px 15px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.08); display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; font-size: 14px;">
        <div><b>📊 IHSG:</b> <span style="color: #fff; font-weight: bold;">{ihsg_price:,.2f}</span></div>
        <div style="color: {'#10b981' if ihsg_change >= 0 else '#ef4444'}; font-weight: bold;">{'+' if ihsg_change >= 0 else ''}{ihsg_change:.2f}%</div>
    </div>
""", unsafe_allow_html=True)

st.title("📈 Screener Saham JII70 & Profit Calculator")

# --- SIDEBAR NAVIGASI & FILTER ---
st.sidebar.header("🧭 Navigasi Menu")
menu = st.sidebar.radio("Pilih Menu:", ["🔍 Screener & Chart 3Bulan", "🧮 Profit Calculator Pro"])

# Fungsi Load Emiten JII70
@st.cache_data
def load_jii70_list():
    try:
        df = pd.read_excel("Daftar Saham JII70.xlsx")
        codes = df['Kode'].dropna().astype(str).str.strip().tolist()
        return codes
    except Exception:
        return [
            "AADI", "ACES", "ADMR", "ADRO", "AKRA", "ANTM", "ARCI", "AVIA", "BKSL", "BRIS", 
            "BRMS", "BSDE", "BTPS", "BUMI", "CMRY", "CPIN", "CTRA", "DEWA", "DKFT", "DSNG", 
            "ELSA", "ENRG", "ERAA", "ESSA", "EXCL", "HEAL", "HRTA", "HRUM", "ICBP", "IMPC", 
            "INDF", "INDY", "INKP", "INTP", "ISAT", "ITMG", "JPFA", "JSMR", "KIJA", "KLBF", 
            "KPIG", "LSIP", "MAPA", "MAPI", "MARK", "MBMA", "MDKA", "MEDC", "MIKA", "MTEL", 
            "MYOR", "PGAS", "PTBA", "RAJA", "RATU", "SIDO", "SMGR", "SMRA", "SRTG", "SSIA", 
            "TAPG", "TCPI", "TINS", "TKIM", "TLKM", "TOBA", "TPIA", "UNTR", "UNVR", "WIFI"
        ]

jii70_codes = load_jii70_list()

# ================= MENU 1: SCREENER & CHART 3 BULAN =================
if menu == "🔍 Screener & Chart 3Bulan":
    st.sidebar.header("⚙️ Filter Parameter Ketat")
    min_value_miliar = st.sidebar.slider("Min. Nilai Transaksi (Miliar Rp)", 0.5, 10.0, 3.0, 0.5)
    vol_multiplier = st.sidebar.slider("Min. Lonjakan Volume (x MA5)", 1.0, 3.0, 1.5, 0.1)
    min_price = st.sidebar.number_input("Harga Minimum (Rp)", min_value=50, max_value=5000, value=200, step=50)

    run_button = st.sidebar.button("🚀 Jalankan Scan Real-Time")

    if run_button:
        with st.spinner("Mengambil data live dari Yahoo Finance & memproses filter teknikal..."):
            tickers = [f"{code}.JK" for code in jii70_codes]
            try:
                # Unduh data 60 hari agar indikator MA20 dan MACD akurat
                data = yf.download(tickers, period="60d", interval="1d", group_by='ticker', progress=False)
            except Exception as e:
                st.error(f"Gagal mengambil data: {e}")
                st.stop()
                
            results = []
            for code in jii70_codes:
                ticker_symbol = f"{code}.JK"
                try:
                    df_stock = data[ticker_symbol].dropna()
                    if len(df_stock) < 25:
                        continue
                    
                    # Hitung MA20
                    df_stock['MA20'] = df_stock['Close'].rolling(window=20).mean()
                    
                    # Hitung MACD (12, 26, 9)
                    exp1 = df_stock['Close'].ewm(span=12, adjust=False).mean()
                    exp2 = df_stock['Close'].ewm(span=26, adjust=False).mean()
                    df_stock['MACD'] = exp1 - exp2
                    df_stock['MACD_Signal'] = df_stock['MACD'].ewm(span=9, adjust=False).mean()
                    
                    latest = df_stock.iloc[-1]
                    prev = df_stock.iloc[-2]
                    
                    close_price = float(latest['Close'])
                    open_price = float(latest['Open'])
                    high_price = float(latest['High'])
                    prev_close = float(prev['Close'])
                    volume = float(latest['Volume'])
                    ma20_val = float(latest['MA20'])
                    macd_val = float(latest['MACD'])
                    macd_sig = float(latest['MACD_Signal'])
                    
                    ma5_vol = df_stock['Volume'].tail(5).mean()
                    val_transaksi = (close_price * volume) / 1e9
                    change_pct = ((close_price - prev_close) / prev_close) * 100
                    vol_spike = volume / ma5_vol if ma5_vol > 0 else 0
                    close_vs_high = close_price / high_price if high_price > 0 else 0
                    
                    # Simulasi / Indikator Akumulasi (Net change 5 hari terakhir > 0)
                    accum_5d = float(df_stock['Close'].iloc[-1] - df_stock['Close'].iloc[-5])
                    
                    # --- LOGIKA FILTER KETAT BSJP ---
                    # 1. Close Hijau (Close > Open)
                    # 2. Harga di atas MA20 (Close > MA20)
                    # 3. Akumulasi > 0 (accum_5d > 0)
                    # 4. MACD Positif (MACD > Signal atau MACD > 0)
                    # 5. Filter standar (Min Price, Min Value, Vol Spike, Close near high)
                    is_close_hijau = close_price > open_price
                    is_above_ma20 = close_price > ma20_val
                    is_accum_positive = accum_5d > 0
                    is_macd_positive = macd_val > macd_sig and macd_val > 0
                    
                    if (close_price >= min_price) and \
                       (val_transaksi >= min_value_miliar) and \
                       (vol_spike >= vol_multiplier) and \
                       (close_vs_high >= 0.985) and \
                       is_close_hijau and \
                       is_above_ma20 and \
                       is_accum_positive and \
                       is_macd_positive:
                        
                        target_jual = int(close_price * 1.025)
                        stop_loss = int(close_price * 0.985)
                        
                        results.append({
                            "Kode": code,
                            "Harga Close": f"Rp {int(close_price):,}",
                            "Perubahan": f"{'+' if change_pct > 0 else ''}{change_pct:.2f}%",
                            "Val Transaksi": f"Rp {val_transaksi:.2f} B",
                            "Vol Spike": f"{vol_spike:.2f}x MA5",
                            "Target Jual": f"Rp {target_jual:,}",
                            "Stop Loss": f"Rp {stop_loss:,}",
                            "Alasan Beli": f"Close Hijau (>Open), Di atas MA20, Akumulasi 5H Positif (+), MACD Bullish (>Signal & >0), Vol Spike {vol_spike:.1f}x.",
                            "Alasan Jual": f"Target Profit +2.5% (Rp {target_jual:,}) atau Stop Loss di bawah Rp {stop_loss:,} esok pagi."
                        })
                except Exception:
                    continue
                    
            st.session_state['df_result'] = pd.DataFrame(results)

    # Tampilkan Hasil Screening jika ada
    if 'df_result' in st.session_state and not st.session_state['df_result'].empty:
        st.markdown(f"**✨ Saham Lolos Filter BSJP ({len(st.session_state['df_result'])} Emiten):**")
        st.dataframe(st.session_state['df_result'], use_container_width=True, hide_index=True)
    else:
        st.info("👈 Atur parameter di sidebar lalu klik **'Jalankan Scan Real-Time'**.")

    st.divider()
    
    # --- BAGIAN CHART KECIL & COMPACT DENGAN BB, MACD, STOCH, RSI, VOLUME ---
    st.markdown("##### 📉 Advanced Technical Chart (Candlestick, BB, MACD, Stoch, RSI, Volume)")
    selected_stock = st.selectbox("Pilih Emiten JII70:", jii70_codes)
    
    if selected_stock:
        with st.spinner(f"Memuat chart untuk {selected_stock}..."):
            df_3m = yf.download(f"{selected_stock}.JK", period="3mo", interval="1d", progress=False)
            
            if not df_3m.empty:
                if isinstance(df_3m.columns, pd.MultiIndex):
                    df_3m.columns = df_3m.columns.get_level_values(0)
                
                # Kalkulasi Indikator
                # 1. Bollinger Bands
                df_3m['BB_Middle'] = df_3m['Close'].rolling(window=20).mean()
                df_3m['BB_Std'] = df_3m['Close'].rolling(window=20).std()
                df_3m['BB_Upper'] = df_3m['BB_Middle'] + (df_3m['BB_Std'] * 2)
                df_3m['BB_Lower'] = df_3m['BB_Middle'] - (df_3m['BB_Std'] * 2)
                
                # 2. MACD
                exp1 = df_3m['Close'].ewm(span=12, adjust=False).mean()
                exp2 = df_3m['Close'].ewm(span=26, adjust=False).mean()
                df_3m['MACD'] = exp1 - exp2
                df_3m['MACD_Signal'] = df_3m['MACD'].ewm(span=9, adjust=False).mean()
                df_3m['MACD_Hist'] = df_3m['MACD'] - df_3m['MACD_Signal']
                
                # 3. Stochastic
                low_14 = df_3m['Low'].rolling(window=14).min()
                high_14 = df_3m['High'].rolling(window=14).max()
                df_3m['Stoch_K'] = 100 * ((df_3m['Close'] - low_14) / (high_14 - low_14))
                df_3m['Stoch_D'] = df_3m['Stoch_K'].rolling(window=3).mean()

                # 4. RSI (14)
                delta = df_3m['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                df_3m['RSI'] = 100 - (100 / (1 + rs))

                # Buat Plotly Subplots 5 baris
                fig = make_subplots(
                    rows=5, cols=1, shared_xaxes=True,
                    vertical_spacing=0.02,
                    row_heights=[0.40, 0.12, 0.16, 0.16, 0.16],
                    subplot_titles=(f'{selected_stock} (Candle & BB)', 'Volume', 'MACD', 'Stochastic', 'RSI')
                )

                # Row 1: Candlestick & BB
                fig.add_trace(go.Candlestick(x=df_3m.index, open=df_3m['Open'], high=df_3m['High'], low=df_3m['Low'], close=df_3m['Close'], name='OHLC'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df_3m.index, y=df_3m['BB_Upper'], line=dict(color='rgba(173, 204, 255, 0.4)', width=1), name='BB Upper'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df_3m.index, y=df_3m['BB_Lower'], line=dict(color='rgba(173, 204, 255, 0.4)', width=1), fill='tonexty', fillcolor='rgba(173,204,255, 0.03)', name='BB Lower'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df_3m.index, y=df_3m['BB_Middle'], line=dict(color='orange', width=1), name='MA20'), row=1, col=1)

                # Row 2: Volume
                colors = ['#10b981' if c >= o else '#ef4444' for c, o in zip(df_3m['Close'], df_3m['Open'])]
                fig.add_trace(go.Bar(x=df_3m.index, y=df_3m['Volume'], marker_color=colors, name='Vol'), row=2, col=1)

                # Row 3: MACD
                fig.add_trace(go.Scatter(x=df_3m.index, y=df_3m['MACD'], line=dict(color='#4facfe', width=1), name='MACD'), row=3, col=1)
                fig.add_trace(go.Scatter(x=df_3m.index, y=df_3m['MACD_Signal'], line=dict(color='#f59e0b', width=1), name='Signal'), row=3, col=1)
                fig.add_trace(go.Bar(x=df_3m.index, y=df_3m['MACD_Hist'], marker_color=['#10b981' if val >= 0 else '#ef4444' for val in df_3m['MACD_Hist']], name='Hist'), row=3, col=1)

                # Row 4: Stochastic
                fig.add_trace(go.Scatter(x=df_3m.index, y=df_3m['Stoch_K'], line=dict(color='#00f2fe', width=1), name='%K'), row=4, col=1)
                fig.add_trace(go.Scatter(x=df_3m.index, y=df_3m['Stoch_D'], line=dict(color='#ef4444', width=1), name='%D'), row=4, col=1)

                # Row 5: RSI
                fig.add_trace(go.Scatter(x=df_3m.index, y=df_3m['RSI'], line=dict(color='#a855f7', width=1), name='RSI'), row=5, col=1)

                fig.update_layout(
                    template='plotly_dark',
                    height=600,
                    xaxis_rangeslider_visible=False,
                    margin=dict(l=10, r=10, t=20, b=10),
                    showlegend=False
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Data chart tidak tersedia.")

# ================= MENU 2: PROFIT CALCULATOR PRO (COMPACT) =================
elif menu == "🧮 Profit Calculator Pro":
    st.markdown("##### 🧮 Kalkulator Profit Saham (Compact Pro)")

    col1, col2, col3 = st.columns(3)
    with col1:
        calc_code = st.text_input("Kode Saham", value="TMPO")
        calc_lot = st.number_input("Jumlah Lot", min_value=1, value=51, step=1)
    with col2:
        calc_buy = st.number_input("Buy Price (Rp)", min_value=1, value=173, step=1)
        fee_buy_pct = st.number_input("Fee Beli (%)", min_value=0.0, value=0.15, step=0.01)
    with col3:
        calc_sell = st.number_input("Sell Price (Rp)", min_value=1, value=194, step=1)
        fee_sell_pct = st.number_input("Fee Jual (%)", min_value=0.0, value=0.25, step=0.01)

    # Kalkulasi Finansial
    total_lembar = calc_lot * 100
    gross_buy = total_lembar * calc_buy
    fee_buy_nominal = gross_buy * (fee_buy_pct / 100)
    total_buy_amount = gross_buy + fee_buy_nominal

    gross_sell = total_lembar * calc_sell
    fee_sell_nominal = gross_sell * (fee_sell_pct / 100)
    total_sell_amount = gross_sell - fee_sell_nominal

    net_profit_loss_rp = total_sell_amount - total_buy_amount
    net_profit_loss_pct = (net_profit_loss_rp / total_buy_amount) * 100

    st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)

    res_col1, res_col2, res_col3 = st.columns(3)
    with res_col1:
        st.markdown(f"""
            <div style="background: #161b22; padding: 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); text-align: center;">
                <div style="color: #9ca3af; font-size: 11px; font-weight: bold;">TOTAL BUY (INC. FEE)</div>
                <div style="color: #10b981; font-size: 16px; font-weight: bold; margin-top: 3px;">Rp {total_buy_amount:,.0f}</div>
            </div>
        """, unsafe_allow_html=True)
    with res_col2:
        st.markdown(f"""
            <div style="background: #161b22; padding: 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); text-align: center;">
                <div style="color: #9ca3af; font-size: 11px; font-weight: bold;">TOTAL SELL (DEC. FEE)</div>
                <div style="color: #4facfe; font-size: 16px; font-weight: bold; margin-top: 3px;">Rp {total_sell_amount:,.0f}</div>
            </div>
        """, unsafe_allow_html=True)
    with res_col3:
        color_pl = "#10b981" if net_profit_loss_rp >= 0 else "#ef4444"
        st.markdown(f"""
            <div style="background: #161b22; padding: 10px; border-radius: 8px; border: 1px solid {color_pl}; text-align: center;">
                <div style="color: #9ca3af; font-size: 11px; font-weight: bold;">NET PROFIT / LOSS</div>
                <div style="color: {color_pl}; font-size: 16px; font-weight: bold; margin-top: 3px;">
                    {'+' if net_profit_loss_rp >= 0 else ''}Rp {net_profit_loss_rp:,.0f} ({'+' if net_profit_loss_pct >= 0 else ''}{net_profit_loss_pct:.2f}%)
                </div>
            </div>
        """, unsafe_allow_html=True)