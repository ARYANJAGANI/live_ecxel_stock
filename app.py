from flask import Flask, render_template, jsonify, request
import pandas as pd
import os
from datetime import datetime
import json

app = Flask(__name__)

def read_excel_data():
    """Read and process the Excel file"""
    try:
        # Read Excel file with proper headers
        df = pd.read_excel('LIVE.xls', header=7)
        
        # Clean the data
        df = df.dropna(subset=[df.columns[0]])  # Remove rows with no scrip name
        df = df[df[df.columns[0]] != 'Scrip Name']  # Remove any duplicate headers
        
        # Columns are already named correctly from the Excel file
        # Just convert numeric columns
        numeric_columns = ['% Change', 'Bid Price', 'Offer Price', 'Open', 'High', 'Low', 'Close', 'Current', 'Qty', 'Open Interest']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df.to_dict('records')
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return []

def get_recommendation(stock_data):
    """Generate buy/sell recommendation based on stock data"""
    try:
        change_percent = float(stock_data.get('% Change', 0))
        bid_price = float(stock_data.get('Bid Price', 0))
        offer_price = float(stock_data.get('Offer Price', 0))
        current_price = float(stock_data.get('Current', 0))
        
        # Simple recommendation logic
        if change_percent > 2:
            return {"action": "BUY", "reason": f"Strong upward momentum (+{change_percent:.2f}%)", "confidence": "High"}
        elif change_percent > 1:
            return {"action": "BUY", "reason": f"Positive momentum (+{change_percent:.2f}%)", "confidence": "Medium"}
        elif change_percent < -2:
            return {"action": "SELL", "reason": f"Strong downward momentum ({change_percent:.2f}%)", "confidence": "High"}
        elif change_percent < -1:
            return {"action": "SELL", "reason": f"Negative momentum ({change_percent:.2f}%)", "confidence": "Medium"}
        else:
            return {"action": "HOLD", "reason": f"Stable movement ({change_percent:.2f}%)", "confidence": "Medium"}
    except:
        return {"action": "HOLD", "reason": "Insufficient data for recommendation", "confidence": "Low"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stocks')
def get_stocks():
    """Get all stocks data"""
    stocks = read_excel_data()
    return jsonify(stocks)

@app.route('/api/search')
def search_stock():
    """Search for a specific stock"""
    query = request.args.get('q', '').upper()
    if not query:
        return jsonify({"error": "No search query provided"})
    
    stocks = read_excel_data()
    
    # Search for stocks matching the query
    matching_stocks = []
    for stock in stocks:
        scrip_name = str(stock.get('Scrip Name', '')).upper()
        if query in scrip_name:
            # Add recommendation to the stock data
            stock['recommendation'] = get_recommendation(stock)
            matching_stocks.append(stock)
    
    return jsonify(matching_stocks)

@app.route('/api/stock/<stock_name>')
def get_stock_detail(stock_name):
    """Get detailed information for a specific stock"""
    stock_name = stock_name.upper()
    stocks = read_excel_data()
    
    for stock in stocks:
        if str(stock.get('Scrip Name', '')).upper() == stock_name:
            stock['recommendation'] = get_recommendation(stock)
            stock['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            return jsonify(stock)
    
    return jsonify({"error": "Stock not found"})

if __name__ == '__main__':
    print("Starting Live Stock Monitor...")
    print("Open your browser and go to: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    app.run(debug=False, host='127.0.0.1', port=5000)
