import os
import smtplib
import ssl
import tempfile
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import plotly.graph_objects as go
import pandas as pd
import plotly.io as pio

import yfinance as yf
from plotly.subplots import make_subplots

CHART_DATA = {
    "UNG": {
        "title": "US Natural Gas Fund (UNG)"
    },
    "UGA": {
        "title": "US Gasoline Fund (UGA)"
    }
}


def build_chart(ticker, chart_title, name_dir):
    ticker_data = yf.Ticker(ticker)
    df = ticker_data.history(period="1mo")

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Candlestick(x=df.index,
                                 open=df['Open'], high=df['High'],
                                 low=df['Low'], close=df['Close']),
                  secondary_y=False)

    dt_all = pd.date_range(start=df.index[0], end=df.index[-1])
    dt_obs = [d.strftime("%Y-%m-%d") for d in pd.to_datetime(df.index)]
    dt_breaks = [d for d in dt_all.strftime("%Y-%m-%d").tolist() if d not in dt_obs]

    fig.update_layout(title=chart_title, xaxis_rangeslider_visible=False, showlegend=False)
    fig.add_trace(go.Bar(x=df.index, y=df['Volume']),
                  secondary_y=True)
    fig.update_yaxes(range=[0, max(df["Volume"]) * 6], secondary_y=True)
    fig.update_yaxes(range=[min(df["Low"]) * .9, max(df["High"]) * 1.02], secondary_y=False)
    fig.update_xaxes(rangebreaks=[dict(values=dt_breaks)])

    pio.write_image(fig, name_dir, width=1200, height=675)


def send_email(recipient, tempdir):
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls(context=ssl.create_default_context())
    server.login("coinsvtapi@gmail.com", "5y&dt7{*+WYPX/nr")
    message = MIMEMultipart()
    message["From"] = "coinsvtapi@gmail.com"
    message["To"] = recipient
    message["Subject"] = "COINS Weekly Charts"
    body = "These are the weekly COINS charts"
    for chart_name in os.listdir(tempdir):
        with open(tempdir + "\\" + chart_name, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {chart_name}",
            )
            message.attach(part)

    message.attach(MIMEText(body, "plain"))
    server.sendmail("coinsvtapi@gmail.com", recipient, message.as_string())


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmpdirname:
        for chart in CHART_DATA:
            build_chart(chart, CHART_DATA[chart]["title"], tmpdirname + "\\" + chart + ".png")
        send_email("promalcolm@gmail.com", tmpdirname)
