#!/usr/bin/env python3
"""
Script to extract Spark UI metrics via REST API and populate project_metrics_log.csv
"""

import requests
import csv
import datetime
from typing import Dict, List

# Spark UI REST API endpoint
SPARK_UI_URL = "http://localhost:4040"

def get_sql_queries() -> List[Dict]:
    """Fetch all SQL queries from Spark UI"""
    try:
        response = requests.get(f"{SPARK_UI_URL}/api/v1/applications")
        if response.status_code != 200:
            print(f"Error: Cannot connect to Spark UI at {SPARK_UI_URL}")
            return []
        
        apps = response.json()
        if not apps:
            print("No Spark applications found")
            return []
        
        app_id = apps[0]['id']
        sql_response = requests.get(f"{SPARK_UI_URL}/api/v1/applications/{app_id}/sql")
        
        if sql_response.status_code == 200:
            return sql_response.json()
        else:
            print(f"Error fetching SQL queries: {sql_response.status_code}")
            return []
    except Exception as e:
        print(f"Error connecting to Spark UI: {e}")
        return []

def get_query_details(query_id: int) -> Dict:
    """Fetch detailed metrics for a specific SQL query"""
    try:
        response = requests.get(f"{SPARK_UI_URL}/api/v1/applications")
        apps = response.json()
        app_id = apps[0]['id']
        
        detail_response = requests.get(
            f"{SPARK_UI_URL}/api/v1/applications/{app_id}/sql/{query_id}"
        )
        
        if detail_response.status_code == 200:
            return detail_response.json()
        else:
            return {}
    except Exception as e:
        print(f"Error fetching query {query_id} details: {e}")
        return {}

def extract_metrics(query_data: Dict) -> Dict:
    """Extract relevant metrics from query data"""
    metrics = {
        'elapsed_ms': query_data.get('duration', 0),
        'input_size_bytes': 0,
        'shuffle_read_bytes': 0,
        'shuffle_write_bytes': 0,
        'files_read': 0
    }
    
    # Parse metrics from stages
    for stage_id in query_data.get('stageIds', []):
        try:
            response = requests.get(f"{SPARK_UI_URL}/api/v1/applications")
            apps = response.json()
            app_id = apps[0]['id']
            
            stage_response = requests.get(
                f"{SPARK_UI_URL}/api/v1/applications/{app_id}/stages/{stage_id}"
            )
            
            if stage_response.status_code == 200:
                stages = stage_response.json()
                for stage in stages:
                    task_metrics = stage.get('taskMetrics', {})
                    
                    # Input metrics
                    input_metrics = task_metrics.get('inputMetrics', {})
                    metrics['input_size_bytes'] += input_metrics.get('bytesRead', 0)
                    metrics['files_read'] += input_metrics.get('recordsRead', 0)
                    
                    # Shuffle read metrics
                    shuffle_read = task_metrics.get('shuffleReadMetrics', {})
                    metrics['shuffle_read_bytes'] += shuffle_read.get('remoteBytesRead', 0)
                    metrics['shuffle_read_bytes'] += shuffle_read.get('localBytesRead', 0)
                    
                    # Shuffle write metrics
                    shuffle_write = task_metrics.get('shuffleWriteMetrics', {})
                    metrics['shuffle_write_bytes'] += shuffle_write.get('bytesWritten', 0)
        except Exception as e:
            print(f"Error extracting stage {stage_id} metrics: {e}")
    
    return metrics

def identify_query_type(description: str, query_id: int) -> tuple:
    """Identify which query (Q1/Q2/Q3) and phase (baseline/optimized) based on query ID"""
    # Query IDs mapping (adjust based on your execution order):
    # Baseline queries are typically executed first, then optimized
    # Pattern: Q1_baseline, Q2_baseline, Q3_baseline, Q1_opt, Q2_opt, Q3_opt
    
    query_map = {
        # Baseline queries (from cell 11)
        7: ('Q1', 'baseline'),
        8: ('Q2', 'baseline'),
        9: ('Q3', 'baseline'),
        # Optimized queries (from cell 13)
        13: ('Q1', 'optimized'),
        14: ('Q2', 'optimized'),
        15: ('Q3', 'optimized'),
    }
    
    return query_map.get(query_id, ('Unknown', 'Unknown'))

def main():
    print("Connecting to Spark UI...")
    queries = get_sql_queries()
    
    if not queries:
        print("No queries found. Make sure Spark is running and UI is accessible.")
        return
    
    print(f"Found {len(queries)} SQL queries")
    
    # Filter relevant queries (exclude internal Spark operations)
    relevant_queries = []
    for q in queries:
        query_id = q.get('id')
        description = q.get('description', '')
        
        # Identify if this is one of our Q1/Q2/Q3 queries
        query_name, phase = identify_query_type(description, query_id)
        
        if query_name != 'Unknown':
            relevant_queries.append({
                'id': query_id,
                'query': query_name,
                'phase': phase,
                'description': description,
                'duration': q.get('duration', 0)
            })
    
    if not relevant_queries:
        print("\nNo Q1/Q2/Q3 queries identified. Available queries:")
        for q in queries:
            print(f"  ID {q.get('id')}: {q.get('description', 'N/A')[:80]}")
        print("\nPlease update query_map in the script with correct IDs.")
        return
    
    print(f"\nIdentified {len(relevant_queries)} relevant queries:")
    for rq in relevant_queries:
        print(f"  ID {rq['id']}: {rq['query']} ({rq['phase']}) - {rq['duration']}ms")
    
    # Collect detailed metrics
    csv_rows = []
    for rq in relevant_queries:
        print(f"\nExtracting metrics for {rq['query']} ({rq['phase']})...")
        details = get_query_details(rq['id'])
        metrics = extract_metrics(details)
        
        csv_row = {
            'run_id': f"run_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'query': rq['query'],
            'phase': rq['phase'],
            'files_read': metrics['files_read'],
            'input_size_bytes': metrics['input_size_bytes'],
            'shuffle_read_bytes': metrics['shuffle_read_bytes'],
            'shuffle_write_bytes': metrics['shuffle_write_bytes'],
            'elapsed_ms': rq['duration'],
            'notes': f"Extracted from Spark UI query ID {rq['id']}",
            'timestamp': datetime.datetime.now().isoformat()
        }
        csv_rows.append(csv_row)
        
        print(f"  Duration: {csv_row['elapsed_ms']}ms")
        print(f"  Input: {csv_row['input_size_bytes']:,} bytes")
        print(f"  Shuffle read: {csv_row['shuffle_read_bytes']:,} bytes")
        print(f"  Shuffle write: {csv_row['shuffle_write_bytes']:,} bytes")
    
    # Write to CSV
    csv_file = 'project_metrics_log.csv'
    
    # Read existing header
    try:
        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
    except:
        header = ['run_id', 'query', 'phase', 'files_read', 'input_size_bytes',
                  'shuffle_read_bytes', 'shuffle_write_bytes', 'elapsed_ms', 
                  'notes', 'timestamp']
    
    # Write data
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(csv_rows)
    
    print(f"\nMetrics saved to {csv_file}")
    print(f"   Total rows: {len(csv_rows)}")

if __name__ == "__main__":
    main()
