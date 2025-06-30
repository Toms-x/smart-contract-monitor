
# This file will contain all the API endpoints for the  dashboard.

import sqlite3
import datetime
import math
import os
from openai import OpenAI
from flask import Blueprint, jsonify, request

# A Blueprint helps organize a group of related views and other code.
api_bp = Blueprint('api', __name__, url_prefix='/api')

DATABASE_FILE = 'events.db'

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    API endpoint to fetch the overview statistics.
    WITH DETAILED LOGGING FOR DEBUGGING.
    """
    print("\n--- [DEBUG] /api/stats endpoint called ---")
    try:
        token_symbol = request.args.get('token', 'USDC')
        print(f"[DEBUG] Token symbol: {token_symbol}")
        
        print("[DEBUG] Connecting to database...")
        conn = get_db_connection()
        cursor = conn.cursor()
        print("[DEBUG] Database connection successful.")

        print("[DEBUG] Querying for latest block...")
        latest_block_query = "SELECT MAX(blockNumber) as latest_block FROM events"
        cursor.execute(latest_block_query)
        latest_block = cursor.fetchone()['latest_block'] or 0
        print(f"[DEBUG] Latest block found: {latest_block}")

        twenty_four_hours_ago = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        
        print("[DEBUG] Querying for 24h transaction count...")
        tx_count_query = "SELECT COUNT(*) as count FROM events WHERE timestamp >= ?"
        cursor.execute(tx_count_query, (twenty_four_hours_ago,))
        total_transactions_24h = cursor.fetchone()['count'] or 0
        print(f"[DEBUG] 24h transaction count: {total_transactions_24h}")

        print(f"[DEBUG] Querying for 24h volume for {token_symbol}...")
        volume_query = "SELECT SUM(value) as total_volume FROM events WHERE timestamp >= ? AND tokenSymbol = ?"
        cursor.execute(volume_query, (twenty_four_hours_ago, token_symbol))
        total_volume_24h = cursor.fetchone()['total_volume'] or 0
        print(f"[DEBUG] 24h volume: {total_volume_24h}")

        conn.close()
        print("[DEBUG] Database connection closed.")

        stats_data = {"total_transactions_24h": total_transactions_24h, "total_volume_24h": total_volume_24h, "latest_block": latest_block, "token_symbol": token_symbol}
        
        print("[DEBUG] Successfully prepared JSON response. Sending to browser.")
        return jsonify(stats_data)
        
    except Exception as e:
        # This will now print the exact error to your terminal
        print(f"\n--- [ERROR] An error occurred in /api/stats: {e} ---\n")
        return jsonify({"error": "A server error occurred"}), 500


@api_bp.route('/events', methods=['GET'])
def get_events():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('limit', 10, type=int)
        offset = (page - 1) * per_page
        from_address = request.args.get('from_address')
        to_address = request.args.get('to_address')
        conn = get_db_connection()
        cursor = conn.cursor()
        base_query = "FROM events"
        count_query = "SELECT COUNT(*) as count " + base_query
        events_query = "SELECT * " + base_query
        conditions = []
        params = []
        if from_address:
            conditions.append("from_address = ?")
            params.append(from_address)
        if to_address:
            conditions.append("to_address = ?")
            params.append(to_address)
        if conditions:
            where_clause = " WHERE " + " AND ".join(conditions)
            count_query += where_clause
            events_query += where_clause
        cursor.execute(count_query, tuple(params))
        total_events = cursor.fetchone()['count'] or 0
        total_pages = math.ceil(total_events / per_page)
        events_query += " ORDER BY blockNumber DESC, id DESC LIMIT ? OFFSET ?"
        final_params = tuple(params + [per_page, offset])
        cursor.execute(events_query, final_params)
        events_rows = cursor.fetchall()
        conn.close()
        events_list = [dict(row) for row in events_rows]
        response_data = {"pagination": {"current_page": page, "total_items": total_events, "total_pages": total_pages, "per_page": per_page, "has_next": page < total_pages, "has_prev": page > 1}, "events": events_list}
        return jsonify(response_data)
    except Exception as e:
        print(f"Error in /events: {e}")
        return jsonify({"error": "A database error occurred"}), 500


@api_bp.route('/analytics/volume-by-block', methods=['GET'])
def get_volume_by_block():
    try:
        limit = 50 
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT blockNumber, SUM(value) as totalVolume FROM events GROUP BY blockNumber ORDER BY blockNumber DESC LIMIT ?"
        cursor.execute(query, (limit,))
        data_rows = cursor.fetchall()
        conn.close()
        labels = [row['blockNumber'] for row in data_rows]
        data = [row['totalVolume'] for row in data_rows]
        labels.reverse()
        data.reverse()
        chart_data = { "labels": labels, "data": data }
        return jsonify(chart_data)
    except Exception as e:
        print(f"Error in /analytics/volume-by-block: {e}")
        return jsonify({"error": "A database error occurred"}), 500


# API ENDPOINT FOR AI QUERIES
@api_bp.route('/ai-query', methods=['POST'])
def handle_ai_query():
    """
    Handles natural language queries by sending them to OpenAI's API
    to generate an SQL query, then executes it.
    """
    # 1. Configure the OpenAI client
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    except Exception as e:
        print(f"Error configuring OpenAI client: {e}")
        return jsonify({"error": "OpenAI client could not be configured. Check your API key."}), 500

    query_text = request.json.get('query', '').lower()
    if not query_text:
        return jsonify({"error": "Query cannot be empty."}), 400

    # 2. Define the system prompt for the AI
    # This is the most important part. It tells the AI its role and constraints.
    system_prompt = f"""
    You are an expert SQLite database assistant. A user will ask you a question in plain English.
    Your only job is to convert that question into a single, valid SQLite query for a table named 'events'.
    The table 'events' has the following columns: id, tx_hash, blockNumber, timestamp, from_address, to_address, value, tokenSymbol.
    - The 'value' column is a number representing the transaction amount.
    - The 'timestamp' is a string in 'YYYY-MM-DD HH:MM:SS' format.
    - ONLY output the SQL query. Do not include any other text, explanation, or markdown formatting.
    - IMPORTANT: For security, only generate SELECT statements. If the user asks to modify, delete, or drop data, respond with "SELECT 'Error: Your query was denied for security reasons.';".
    """

    try:
        # 3. Call the OpenAI API
        print(f"Sending query to OpenAI: {query_text}")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query_text}
            ],
            temperature=0,
            max_tokens=150
        )
        
        # 4. Extract the SQL query from the AI's response
        sql_query = response.choices[0].message.content.strip()
        print(f"Received SQL from OpenAI: {sql_query}")

        # 5. A crucial security check
        if not sql_query.lower().startswith('select'):
             return jsonify({
                "title": "Query Denied",
                "results": [{"error": "This query was denied for security reasons."}]
            })

        # 6. Execute the generated SQL query
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        conn.close()

        results = [dict(row) for row in rows]
        
        return jsonify({"title": f"Results for: '{query_text}'", "results": results})

    except Exception as e:
        print(f"Error in /ai-query: {e}")
        return jsonify({"error": "An error occurred while processing the AI query."}), 500
