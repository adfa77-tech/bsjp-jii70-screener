import streamlit as st
import pandas as pd
import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from zoneinfo import ZoneInfo

# Konfigurasi Halaman Streamlit (Wide mode)
st.set_page_config(
    page_title="JII70 Syariah Futuristic Pro Terminal",
    page_icon="⚡",
    layout="wide"
)

# Custom CSS untuk Tampilan Futuristik, Padding Atas Aman, & Angka Warna-Warni
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(3, 7, 18, 0.75), rgba(15, 23, 42, 0.85)), 
                    url('https://images.unsplash.com/photo-1506744038136-46273834b3fb?q=80&w=1920&auto=format&fit=crop');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #f8fafc;
    }
    
    /* Menambah jarak atas agar tidak tertutup header Streamlit */
    .block-container {
        padding-top: 4rem;
        padding-bottom: 2rem;
    }
    
    /* Warna Teks Futuristik */
    h1, h2, h3, p, span, label {
        color: #f8fafc !important;
    }
    
    /* Styling Header Tabel */
    thead tr th {
        background-color: #0f172a !important;
        color: #38bdf8 !important;
        font-weight: 900 !important;
        text-align: center !important;
        border-bottom: 2px solid #38bdf8 !important;
    }
    
    /* Jam Realtime WIB Box */
    .clock-box {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid #38bdf8;
        padding: 8px 16px;
        border-radius: 8px;
        color: #38bdf8;
        font-weight: 800;
        font-size: 0.9rem;
        display: inline-block;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.4);
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

# Header Ticker IHSG & Jam WIB
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.85); padding: 12px 20px; border-radius: 10px; border: 1px solid rgba(56,189,248,0.4); display: flex; align-items: center; font-size: 15px; box-shadow: 0 0 15px rgba(56, 189, 248, 0.25);">
            <div><b>📊 IHSG Market:</b> <span style="color: #fff; font-weight: bold;">{ihsg_price:,.2f}</span></div>
            <div style="margin-left: 20px; color: {'#10b981' if ihsg_change >= 0 else '#ef4444'}; font-weight: bold;">{'+' if ihsg_change >= 0 else ''}{ihsg_change:.2f}%</div>
        </div>
    """, unsafe_allow_html=True)

with col_h2:
    waktu_wib = datetime.datetime.now(ZoneInfo("Asia/Jakarta"))
    waktu_str = waktu_wib.strftime("%d %b %Y | %H:%M WIB")
    st.markdown(f'<div style="text-align: right;"><span class="clock-box">🕒 {waktu_str}</span></div>', unsafe_allow_html=True)

st.markdown("""
    <h1 style="margin-top: 15px; font-size: 2.2rem; background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        ⚡ JII70 SYARIAH FUTURISTIC PRO TERMINAL
    </h1>
""", unsafe_allow_html=True)

# --- SIDEBAR NAVIGASI & MENU ---
st.sidebar.header("🧭 Navigasi Menu")
menu = st.sidebar.radio("Pilih Menu:", ["🌐 Semua Saham & Screener", "📈 Chart & Analisis Detail", "🧮 Kalkulator Saham Pro"])

jii70_codes = [
    "AADI", "ACES", "ADMR", "ADRO", "AKRA", "ANTM", "ARCI", "AVIA", "BKSL", "BRIS", 
    "BRMS", "BSDE", "BTPS", "BUMI", "CMRY", "CPIN", "CTRA", "DEWA", "DKFT", "DSNG", 
    "ELSA", "ENRG", "ERAA", "ESSA", "EXCL", "HEAL", "HRTA", "HRUM", "ICBP", "IMPC", 
    "INDF", "INDY", "INKP", "INTP", "ISAT", "ITMG", "JPFA", "JSMR", "KIJA", "KLBF", 
    "KPIG", "LSIP", "MAPA", "MAPI", "MARK", "MBMA", "MDKA", "MEDC", "MIKA", "MTEL", 
    "MYOR", "PGAS", "PTBA", "RAJA", "RATU", "SIDO", "SMGR", "SMRA", "SRTG", "SSIA", 
    "TAPG", "TCPI", "TINS", "TKIM", "TLKM", "TOBA", "TPIA", "UNTR", "UNVR", "WIFI"
]

# ================= MENU 1: SEMUA SAHAM & REKOMENDASI =================
if menu == "🌐 Semua Saham & Screener":
    st.markdown("### 📋 Daftar Semua Saham JII70, Rekomendasi & Analisis Harga")
    
    with st.spinner("Sinkronisasi data real-time seluruh emiten JII70..."):
        tickers = [f"{code}.JK" for code in jii70_codes]
        try:
            data = yf.download(tickers, period="30d", interval="1d", group_by='ticker', progress=False)
        except Exception as e:
            st.error(f"Gagal mengambil data: {e}")
            st.stop()
            
        all_results = []
        for code in jii70_codes:
            ticker_symbol = f"{code}.JK"
            try:
                df_stock = data[ticker_symbol].dropna()
                if len(df_stock) < 15:
                    continue
                
                df_stock['MA20'] = df_stock['Close'].rolling(window=20).mean()
                latest = df_stock.iloc[-1]
                prev = df_stock.iloc[-2]
                
                close_price = float(latest['Close'])
                high_price = float(latest['High'])
                low_price = float(latest['Low'])
                prev_close = float(prev['Close'])
                volume = float(latest['Volume'])
                ma20_val = float(latest['MA20'])
                
                change_pct = ((close_price - prev_close) / prev_close) * 100
                val_transaksi = (close_price * volume) / 1e9
                
                pivot = (high_price + low_price + close_price) / 3
                support = (2 * pivot) - high_price
                resist = (2 * pivot) - low_price
                
                if close_price > ma20_val and change_pct > 1.5:
                    rekomendasi = "Saham Scalping / Momentum"
                    alasan = "Harga di atas MA20 dengan lonjakan persentase positif harian."
                    harga_beli = int(close_price)
                    harga_jual = int(resist)
                    waktu_jual = "Sesi 2 / Hari Ini"
                elif close_price <= support * 1.01:
                    rekomendasi = "Saham BOW (Buy on Weakness)"
                    alasan = "Harga mendekati area support kuat dengan potensi pantulan."
                    harga_beli = int(support)
                    harga_jual = int(pivot)
                    waktu_jual = "1-3 Hari ke Depan"
                else:
                    rekomendasi = "Konsolidasi / Swing"
                    alasan = "Pergerakan harga stabil dalam rentang wajar."
                    harga_beli = int(support)
                    harga_jual = int(resist)
                    waktu_jual = "3-7 Hari"

                all_results.append({
                    "Kode": code,
                    "Close": f"Rp {int(close_price):,}",
                    "Chg%": f"{'+' if change_pct > 0 else ''}{change_pct:.2f}%",
                    "Val (B Rp)": f"Rp {val_transaksi:.2f} B",
                    "Rekomendasi": rekomendasi,
                    "Alasan": alasan,
                    "Harga Beli": f"Rp {harga_beli:,}",
                    "Harga Jual": f"Rp {harga_jual:,}",
                    "Waktu Jual": waktu_jual,
                    "raw_chg": change_pct # Nilai mentah untuk logika warna
                })
            except Exception:
                continue
                
        df_all = pd.DataFrame(all_results)
        if not df_all.empty:
            
            # Fungsi Pewarnaan Angka Warna-Warni Dinamis
            def color_dynamic(row):
                chg = row.get('raw_chg', 0)
                if chg > 0:
                    chg_style = 'background-color: rgba(20, 83, 45, 0.85); color: #4ade80; font-weight: bold;'
                elif chg < 0:
                    chg_style = 'background-color: rgba(127, 29, 29, 0.85); color: #f87171; font-weight: bold;'
                else:
                    chg_style = 'background-color: rgba(30, 41, 59, 0.85); color: #cbd5e1; font-weight: bold;'
                
                return [
                    'background-color: rgba(15, 23, 42, 0.9); color: #38bdf8; font-weight: bold;', # Kode
                    'background-color: rgba(20, 83, 45, 0.85); color: #6ee7b7; font-weight: bold;', # Close
                    chg_style, # Chg%
                    'background-color: rgba(30, 27, 75, 0.85); color: #818cf8;', # Val
                    'background-color: rgba(49, 46, 129, 0.85); color: #c084fc; font-weight: bold;', # Rekomendasi
                    'background-color: rgba(15, 23, 42, 0.85); color: #e2e8f0;', # Alasan
                    'background-color: rgba(6, 78, 59, 0.85); color: #34d399; font-weight: bold;', # Harga Beli
                    'background-color: rgba(88, 28, 135, 0.85); color: #f472b6; font-weight: bold;', # Harga Jual
                    'background-color: rgba(30, 41, 59, 0.85); color: #38bdf8;', # Waktu Jual
                    '' # raw_chg disembunyikan / diabaikan dari styling visual utama
                ]

            # Drop kolom raw_chg untuk tampilan tabel bersih namun gunakan nilainya untuk styling
            display_df = df_all.drop(columns=['raw_chg'])
            styled_df = df_all.style.apply(color_dynamic, axis=1)

            st.dataframe(styled_df, use_container_width=True, height=520)
            
            csv_data = display_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Data ke CSV",
                data=csv_data,
                file_name="jii70_semua_saham_rekomendasi.csv",
                mime="text/csv"
            )
        else:
            st.warning("Data emiten tidak tersedia saat ini.")

# ================= MENU 2: CHART & ANALISIS DETAIL =================
elif menu == "📈 Chart & Analisis Detail":
    st.markdown("### 📉 Advanced Technical Chart (Candlestick, BB, MACD, Stoch, RSI, Volume)")
    selected_stock = st.selectbox("Pilih Emiten JII70:", jii70_codes)
    
    if selected_stock:
        with st.spinner(f"Memuat chart interaktif untuk {selected_stock}..."):
            df_3m = yf.download(f"{selected_stock}.JK", period="3mo", interval="1d", progress=False)
            
            if not df_3m.empty:
                if isinstance(df_3m.columns, pd.MultiIndex):
                    df_3m.columns = df_3m.columns.get_level_values(0)
                
                df_3m['BB_Middle'] = df_3m['Close'].rolling(window=20).mean()
                df_3m['BB_Std'] = df_3m['Close'].rolling(window=20).std()
                df_3m['BB_Upper'] = df_3m['BB_Middle'] + (df_3m['BB_Std'] * 2)
                df_3m['BB_Lower'] = df_3m['BB_Middle'] - (df_3m['BB_Std'] * 2)
                
                exp1 = df_3m['Close'].ewm(span=12, adjust=False).mean()
                exp2 = df_3m['Close'].ewm(span=26, adjust=False).mean()
                df_3m['MACD'] = exp1 - exp2
                df_3m['MACD_Signal'] = df_3m['MACD'].ewm(span=9, adjust=False).mean()
                df_3m['MACD_Hist'] = df_3m['MACD'] - df_3m['MACD_Signal']
                
                low_14 = df_3m['Low'].rolling(window=14).min()
                high_14 = df_3m['High'].rolling(window=14).max()
                df_3m['Stoch_K'] = 100 * ((df_3m['Close'] - low_14) / (high_14 - low_14))
                df_3m['Stoch_D'] = df_3m['Stoch_K'].rolling(window=3).mean()

                delta = df_3m['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                df_3m['RSI'] = 100 - (100 / (1 + rs))

                fig = make_subplots(
                    rows=5, cols=1, shared_xaxes=True,
                    vertical_spacing=0.02,
                    row_heights=[0.40, 0.12, 0.16, 0.16, 0.16],
                    subplot_titles=(f'{selected_stock} (Candle & BB)', 'Volume', 'MACD', 'Stochastic', 'RSI')
                )

                fig.add_trace(go.Candlestick(x=df_3m.index, open=df_3m['Open'], high=df_3m['High'], low=df_3m['Low'], close=df_3m['Close'], name='OHLC'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df_3m.index, y=df_3m['BB_Upper'], line=dict(color='rgba(173, 204, 255, 0.4)', width=1), name='BB Upper'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df_3m.index, y=df_3m['BB_Lower'], line=dict(color='rgba(173, 204, 255, 0.4)', width=1), fill='tonexty', fillcolor='rgba(173,204,255, 0.03)', name='BB Lower'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df_3m.index, y=df_3m['BB_Middle'], line=dict(color='orange', width=1), name='MA20'), row=1, col=1)

                colors = ['#10b981' if c >= o else '#ef4444' for c, o in zip(df_3m['Close'], df_3m['Open'])]
                fig.add_trace(go.Bar(x=df_3m.index, y=df_3m['Volume'], marker_color=colors, name='Vol'), row=2, col=1)

                fig.add_trace(go.Scatter(x=df_3m.index, y=df_3m['MACD'], line=dict(color='#4facfe', width=1), name='MACD'), row=3, col=1)
                fig.add_trace(go.Scatter(x=df_3m.index, y=df_3m['MACD_Signal'], line=dict(color='#f59e0b', width=1), name='Signal'), row=3, col=1)
                fig.add_trace(go.Bar(x=df_3m.index, y=df_3m['MACD_Hist'], marker_color=['#10b981' if val >= 0 else '#ef4444' for val in df_3m['MACD_Hist']], name='Hist'), row=3, col=1)

                fig.add_trace(go.Scatter(x=df_3m.index, y=df_3m['Stoch_K'], line=dict(color='#00f2fe', width=1), name='%K'), row=4, col=1)
                fig.add_trace(go.Scatter(x=df_3m.index, y=df_3m['Stoch_D'], line=dict(color='#ef4444', width=1), name='%D'), row=4, col=1)

                fig.add_trace(go.Scatter(x=df_3m.index, y=df_3m['RSI'], line=dict(color='#a855f7', width=1), name='RSI'), row=5, col=1)

                fig.update_layout(
                    template='plotly_dark',
                    height=650,
                    xaxis_rangeslider_visible=False,
                    margin=dict(l=10, r=10, t=25, b=10),
                    showlegend=False,
                    paper_bgcolor='rgba(15, 23, 42, 0.85)',
                    plot_bgcolor='rgba(15, 23, 42, 0.85)'
                )

                st.plotly_chart(fig, use_container_width=True)

# ================= MENU 3: KALKULATOR SAHAM PRO =================
elif menu == "🧮 Kalkulator Saham Pro":
    st.markdown("### 🧮 Kalkulator Trading & Investasi Saham")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        calc_code = st.selectbox("Nama / Kode Saham", jii70_codes)
        calc_lot = st.number_input("Jumlah Lot", min_value=1, value=10, step=1)
    with col2:
        calc_buy = st.number_input("Harga Beli (Rp)", min_value=1, value=1000, step=10)
        fee_buy_pct = st.number_input("Fee Beli (%)", min_value=0.0, value=0.15, step=0.01)
    with col3:
        calc_sell = st.number_input("Harga Jual (Rp)", min_value=1, value=1050, step=10)
        fee_sell_pct = st.number_input("Fee Jual (%)", min_value=0.0, value=0.25, step=0.01)

    total_lembar = calc_lot * 100
    gross_buy = total_lembar * calc_buy
    fee_buy_nominal = gross_buy * (fee_buy_pct / 100)
    total_buy_amount = gross_buy + fee_buy_nominal

    gross_sell = total_lembar * calc_sell
    fee_sell_nominal = gross_sell * (fee_sell_pct / 100)
    total_sell_amount = gross_sell - fee_sell_nominal

    net_profit_loss_rp = total_sell_amount - total_buy_amount
    net_profit_loss_pct = (net_profit_loss_rp / total_buy_amount) * 100

    st.markdown("<hr style='margin: 15px 0; border-color: rgba(56,189,248,0.2);'>", unsafe_allow_html=True)

    res_col1, res_col2, res_col3 = st.columns(3)
    with res_col1:
        st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.85); padding: 12px; border-radius: 10px; border: 1px solid rgba(56,189,248,0.3); text-align: center;">
                <div style="color: #94a3b8; font-size: 11px; font-weight: bold;">TOTAL MODAL BELI (INC. FEE)</div>
                <div style="color: #38bdf8; font-size: 18px; font-weight: bold; margin-top: 5px;">Rp {total_buy_amount:,.0f}</div>
            </div>
        """, unsafe_allow_html=True)
    with res_col2:
        st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.85); padding: 12px; border-radius: 10px; border: 1px solid rgba(56,189,248,0.3); text-align: center;">
                <div style="color: #94a3b8; font-size: 11px; font-weight: bold;">TOTAL NILAI JUAL (DEC. FEE)</div>
                <div style="color: #818cf8; font-size: 18px; font-weight: bold; margin-top: 5px;">Rp {total_sell_amount:,.0f}</div>
            </div>
        """, unsafe_allow_html=True)
    with res_col3:
        color_pl = "#10b981" if net_profit_loss_rp >= 0 else "#ef4444"
        st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.85); padding: 12px; border-radius: 10px; border: 1px solid {color_pl}; text-align: center;">
                <div style="color: #94a3b8; font-size: 11px; font-weight: bold;">ESTIMASI PROFIT / LOSS BERSIH</div>
                <div style="color: {color_pl}; font-size: 18px; font-weight: bold; margin-top: 5px;">
                    {'+' if net_profit_loss_rp >= 0 else ''}Rp {net_profit_loss_rp:,.0f} ({'+' if net_profit_loss_pct >= 0 else ''}{net_profit_loss_pct:.2f}%)
                </div>
            </div>
        """, unsafe_allow_html=True)
