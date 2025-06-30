
# This file will contain all the API endpoints for the  dashboard.

import sqlite3
import datetime
import math
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
    try:
        token_symbol = request.args.get('token', 'USDC')
        conn = get_db_connection()
        cursor = conn.cursor()
        latest_block_query = "SELECT MAX(blockNumber) as latest_block FROM events"
        cursor.execute(latest_block_query)
        latest_block = cursor.fetchone()['latest_block'] or 0
        twenty_four_hours_ago = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        tx_count_query = "SELECT COUNT(*) as count FROM events WHERE timestamp >= ?"
        cursor.execute(tx_count_query, (twenty_four_hours_ago,))
        total_transactions_24h = cursor.fetchone()['count'] or 0
        volume_query = "SELECT SUM(value) as total_volume FROM events WHERE timestamp >= ? AND tokenSymbol = ?"
        cursor.execute(volume_query, (twenty_four_hours_ago, token_symbol))
        total_volume_24h = cursor.fetchone()['total_volume'] or 0
        conn.close()
        stats_data = {"total_transactions_24h": total_transactions_24h, "total_volume_24h": total_volume_24h, "latest_block": latest_block, "token_symbol": token_symbol}
        return jsonify(stats_data)
    except Exception as e:
        print(f"Error in /stats: {e}")
        return jsonify({"error": "A database error occurred"}), 500


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
    Handles simple, keyword-based "AI" queries.
    This is a simplified version to demonstrate the concept.
    """
    try:
        query_text = request.json.get('query', '').lower()

        conn = get_db_connection()
        cursor = conn.cursor()
        
        response_title = "AI Insight"
        sql_query = ""
        
        # Keyword-based routing for the query
        if 'whale' in query_text or 'largest' in query_text or 'biggest' in query_text:
            response_title = "Top 5 Largest Transfers"
            sql_query = "SELECT * FROM events ORDER BY value DESC LIMIT 5"
        elif 'latest' in query_text or 'newest' in query_text:
            response_title = "5 Most Recent Transfers"
            sql_query = "SELECT * FROM events ORDER BY blockNumber DESC, id DESC LIMIT 5"
        elif 'consolidation' in query_text:
            response_title = "Potential Consolidation Addresses"
            # This query finds addresses that have received funds more than 5 times
            sql_query = """
                SELECT to_address, COUNT(*) as tx_count 
                FROM events 
                GROUP BY to_address 
                HAVING tx_count > 5 
                ORDER BY tx_count DESC 
                LIMIT 5
            """
        else:
            return jsonify({
                "title": "Query Not Understood",
                "results": [{"error": "Sorry, I can only understand queries about 'largest', 'latest', or 'consolidation' transfers for now."}]
            })

        cursor.execute(sql_query)
        rows = cursor.fetchall()
        conn.close()

        results = [dict(row) for row in rows]

        return jsonify({"title": response_title, "results": results})

    except Exception as e:
        print(f"Error in /ai-query: {e}")
        return jsonify({"error": "An error occurred while processing the AI query."}), 500