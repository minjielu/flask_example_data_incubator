from flask import Flask, render_template, request, redirect
import numpy as np
import pandas as pd
import sys
from datetime import datetime
from dateutil.relativedelta import relativedelta
from bokeh.plotting import figure
from bokeh.models import DatetimeTickFormatter
import json
from bokeh.embed import json_item
from bokeh.resources import CDN

app = Flask(__name__)

@app.route('/')
def index():
    with open('data/tickers.txt', 'r') as file:
        tickers = file.read().split('\n')
    tickers = '###'.join(tickers) # Pass the names of tickers separated by '###'
    return render_template('index.html', tickers=tickers)

@app.route('/plot', methods=["POST"])
def about():
    type_mapping = {'Closing Price':'close', 'Adjusted Closing Price':'adj_close', \
                    'Open Price':'open', 'Adjusted Open Price':'adj_open'}
    ticker = request.form.get("name")
    ticker = ticker.split('-')[0] # get rid of the company full name.
    type = request.form.get("type")
    column = type_mapping[type] # get the name of the column needed.
    range = request.form.get("range")
    # Get the data for the ticker.
    query = "https://www.quandl.com/api/v3/datatables/WIKI/PRICES.csv?ticker=" \
            +ticker \
            +"&qopts.columns=date," \
            +column \
            +"&api_key=ym9raNgKxyW-vx79qY5z"
    time_series = pd.read_csv(query)
    time_series['date'] = pd.to_datetime(time_series['date']) # Transfer the date column to timestamp to be safe.
    latest = time_series['date'].max() # The latest date.

    # Find the rows within the date range specified by the user.
    starting = None
    if range == '1 month':
        starting = latest-relativedelta(months=1)
    elif range == '6 months':
        starting = latest-relativedelta(months=6)
    elif range == 'YTD':
        starting = datetime(latest.year,1,1)
    elif range == '1 year':
        starting = latest-relativedelta(years=1)
    elif range == '5 years':
        starting = latest-relativedelta(years=5)
    time_series = time_series[time_series['date'] >= starting]

    p = figure(plot_width=580, plot_height=520, x_axis_type='datetime')
    p.xaxis.formatter=DatetimeTickFormatter(
        days=["%b %d"],
        months=["%b %Y"],
        years=["%b %Y"],
    )
    # add a line renderer
    p.line(x='date', y=column, source=time_series, line_width=2, legend=ticker+': '+type)
    p.title.text = 'Quandl WIKI Stock Prices'
    p.xaxis.axis_label = 'date'
    p.legend.location = "top_left" # Set the position of the legend
    p = json.dumps(json_item(p))
    return render_template('plot.html', p=p, resources=CDN.render())

if __name__ == '__main__':
    app.run(port=33507)
