from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import yfinance as yf, pandas as pd, numpy as np, plotly.graph_objects as go

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def live():
    df = yf.download("GC=F", period="10d", interval="60m", auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.reset_index()
    df["MA200"] = df["Close"].rolling(200).mean()
    
    # Hitung sudut 80
    x = np.arange(50)
    last = df.tail(50)
    slope = np.polyfit(x, last["Close"], 1)[0]
    angle = float(np.degrees(np.arctan(slope / (last["Close"].mean()*0.01))))
    
    p = float(df["Close"].iloc[-1])
    ma = float(df["MA200"].iloc[-1])
    low20 = float(df["Low"].tail(20).min())
    
    is_buy = angle >= 78 and p > ma
    sl = min(ma, low20) - 6
    tf1 = p + 15
    tf2 = p + 35
    tf3 = p + 70
    
    color = "#00ff88" if is_buy else "#ffcc00"
    status = "🚀 BUY SAKTI GARIS 80 AKTIF" if is_buy else f"⏳ WAIT - SUDUT {angle:.1f}°"
    box = f"ENTRY {p:.1f} | SL {sl:.1f} | TF1 {tf1:.1f} TF2 {tf2:.1f} TF3 {tf3:.1f}" if is_buy else f"HARGA {p:.1f} | MA200 {ma:.1f}"
    
    fig = go.Figure(data=[go.Candlestick(
        x=df["Date"] if "Date" in df.columns else df.index,
        open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"])])
    fig.update_layout(template="plotly_dark", height=600, xaxis_rangeslider_visible=False, paper_bgcolor="black", plot_bgcolor="black")
    
    if is_buy:
        fig.add_hline(y=p, line_color="lime", annotation_text=f"ENTRY {p:.1f}")
        fig.add_hline(y=sl, line_color="red", line_dash="dot", annotation_text=f"SL {sl:.1f}")
        fig.add_hline(y=tf1, line_color="cyan", annotation_text=f"TF1 {tf1:.1f}")
        fig.add_hline(y=tf2, line_color="cyan", annotation_text=f"TF2 {tf2:.1f}")
        fig.add_hline(y=tf3, line_color="gold", annotation_text=f"TF3 {tf3:.1f}")
    
    chart = fig.to_html(full_html=False, include_plotlyjs='cdn')
    return f"<html><meta name='viewport' content='width=device-width'><body style='background:black;margin:0'><div style='background:{color};padding:15px;text-align:center;font-weight:bold'>{status}<br>{box}</div>{chart}<script>setTimeout(()=>location.reload(),30000)</script></body></html>"
