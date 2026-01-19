# -*- coding: utf-8 -*-
"""
SMSS 가계부 - 웹 서버
웹에서 직접 지출을 입력하고 저장할 수 있습니다.
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__, static_folder='.')
CORS(app)

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data.json')

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'expenses': [],
        'summary': {
            'total_expenses': 0,
            'total_transactions': 0,
            'category_breakdown': {},
            'payment_method_breakdown': {},
            'monthly_totals': {}
        },
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def save_data(data):
    data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def recalculate_summary(data):
    expenses = data['expenses']

    category_breakdown = {}
    payment_breakdown = {}
    monthly_totals = {}

    for exp in expenses:
        amount = exp['amount']
        cat = exp['category']
        payment = exp['payment_method']
        month_key = f"{exp['year']}-{exp['month']:02d}"

        # Category
        category_breakdown[cat] = category_breakdown.get(cat, 0) + amount

        # Payment
        payment_breakdown[payment] = payment_breakdown.get(payment, 0) + amount

        # Monthly
        if month_key not in monthly_totals:
            monthly_totals[month_key] = {'total': 0, 'categories': {}}
        monthly_totals[month_key]['total'] += amount
        monthly_totals[month_key]['categories'][cat] = monthly_totals[month_key]['categories'].get(cat, 0) + amount

    data['summary'] = {
        'total_expenses': sum(e['amount'] for e in expenses),
        'total_transactions': len(expenses),
        'category_breakdown': category_breakdown,
        'payment_method_breakdown': payment_breakdown,
        'monthly_totals': monthly_totals
    }
    return data

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/data.json')
def get_data():
    return jsonify(load_data())

@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    return jsonify(load_data())

@app.route('/api/expenses', methods=['POST'])
def add_expense():
    data = load_data()
    expense = request.json

    # Generate unique ID
    expense['id'] = datetime.now().strftime('%Y%m%d%H%M%S%f')

    # Parse date
    date_parts = expense['date'].split('-')
    expense['year'] = int(date_parts[0])
    expense['month'] = int(date_parts[1])

    data['expenses'].append(expense)
    data = recalculate_summary(data)
    save_data(data)

    return jsonify({'success': True, 'expense': expense})

@app.route('/api/expenses/<expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    data = load_data()
    data['expenses'] = [e for e in data['expenses'] if e.get('id') != expense_id]
    data = recalculate_summary(data)
    save_data(data)

    return jsonify({'success': True})

@app.route('/api/expenses/<expense_id>', methods=['PUT'])
def update_expense(expense_id):
    data = load_data()
    updated = request.json

    for i, exp in enumerate(data['expenses']):
        if exp.get('id') == expense_id:
            updated['id'] = expense_id
            date_parts = updated['date'].split('-')
            updated['year'] = int(date_parts[0])
            updated['month'] = int(date_parts[1])
            data['expenses'][i] = updated
            break

    data = recalculate_summary(data)
    save_data(data)

    return jsonify({'success': True})

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'

    if debug:
        print("=" * 50)
        print("SMSS 가계부 대시보드")
        print("=" * 50)
        print(f"\n서버 시작: http://localhost:{port}")
        print("브라우저에서 위 주소로 접속하세요.")
        print("\n서버를 종료하려면 Ctrl+C를 누르세요.")
        print("=" * 50)
        import webbrowser
        webbrowser.open(f'http://localhost:{port}')

    app.run(host='0.0.0.0', port=port, debug=debug)
