import pandas as pd
import os
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(__file__), '../data')

# Data quality tracking
anomalies = []

def load_and_process_data():
    """Load all CSV files and compute operational metrics"""
    global anomalies
    anomalies = []
    
    print('Reading CSV files...')
    
    # Read all CSV files
    robots_df = pd.read_csv(os.path.join(DATA_DIR, 'robots.csv'))
    telemetry_df = pd.read_csv(os.path.join(DATA_DIR, 'telemetry.csv'))
    interactions_df = pd.read_csv(os.path.join(DATA_DIR, 'interactions.csv'))
    nav_events_df = pd.read_csv(os.path.join(DATA_DIR, 'nav_events.csv'))
    vending_df = pd.read_csv(os.path.join(DATA_DIR, 'vending.csv'))
    footfall_df = pd.read_csv(os.path.join(DATA_DIR, 'footfall.csv'))
    
    print('Cleaning data...')
    
    # Data cleaning
    # Normalize telemetry states
    telemetry_df['state'] = telemetry_df['state'].fillna('unknown').str.lower()
    
    # Normalize footfall zones (fix underscores)
    footfall_issues = footfall_df[footfall_df['zone'].str.contains('_', na=False)]
    if len(footfall_issues) > 0:
        anomalies.append({
            'type': 'zone_name_inconsistency',
            'entity': 'footfall.csv',
            'note': f'{len(footfall_issues)} rows have zone names with underscores (e.g., PDD_A) instead of dashes (PDD-A)'
        })
        footfall_df['zone'] = footfall_df['zone'].str.replace('_', '-')
    
    # Check for missing severity in nav events
    missing_severity = nav_events_df[nav_events_df['severity'].isna()]
    if len(missing_severity) > 0:
        anomalies.append({
            'type': 'missing_field',
            'entity': 'nav_events.csv',
            'note': f'{len(missing_severity)} navigation events missing severity field'
        })
    
    # Check for unregistered (ghost) robots in telemetry
    registered_ids = set(robots_df['robot_id'])
    telemetry_ids = set(telemetry_df['robot_id'])
    ghost_ids = sorted(telemetry_ids - registered_ids)
    if ghost_ids:
        anomalies.append({
            'type': 'unregistered_robot',
            'entity': ', '.join(ghost_ids),
            'note': f'{len(ghost_ids)} robot id(s) appear in telemetry but are not in robots.csv ({", ".join(ghost_ids)}); excluded from fleet metrics'
        })
    
    # Calculate metrics
    metrics = calculate_metrics(
        robots_df, telemetry_df, interactions_df, 
        nav_events_df, vending_df, footfall_df
    )
    
    return {
        'summary': metrics['summary'],
        'robots': metrics['robot_details'],
        'zones': metrics['zone_metrics'],
        'dataQuality': {
            'anomalies': anomalies,
            'totalRecords': {
                'robots': len(robots_df),
                'telemetry': len(telemetry_df),
                'interactions': len(interactions_df),
                'navEvents': len(nav_events_df),
                'vending': len(vending_df),
                'footfall': len(footfall_df)
            }
        },
        'rawMetrics': metrics['raw_metrics']
    }

def calculate_metrics(robots_df, telemetry_df, interactions_df, nav_events_df, vending_df, footfall_df):
    """Calculate all operational metrics"""
    
    # Pilot period
    PILOT_START = datetime(2026, 6, 1)
    PILOT_END = datetime(2026, 6, 14)
    PILOT_DAYS = 14
    
    # Summary metrics
    total_robots = len(robots_df)
    
    # Active robots: registered robots with any telemetry data
    # (ghost ids in telemetry but not in robots.csv are excluded)
    registered_ids = set(robots_df['robot_id'])
    active_robot_ids = set(telemetry_df['robot_id']) & registered_ids
    active_robots = len(active_robot_ids)
    
    # QR metrics
    qr_scans = interactions_df[interactions_df['type'] == 'qr_scan']
    # Handle boolean conversion
    qr_conversions = qr_scans[
        (qr_scans['converted'] == 'true') | 
        (qr_scans['converted'] == True) | 
        (qr_scans['converted'] == 1)
    ]
    total_scans = len(qr_scans)
    conversions = len(qr_conversions)
    conversion_rate = conversions / total_scans if total_scans > 0 else 0
    
    # Vending metrics
    vending_paid = vending_df[vending_df['payment_status'] == 'paid']
    total_revenue = vending_paid['amount'].astype(float).sum()
    transactions_counted = len(vending_paid)
    
    # Per-robot details
    robot_details = []
    for _, robot in robots_df.iterrows():
        robot_id = robot['robot_id']
        
        robot_telem = telemetry_df[telemetry_df['robot_id'] == robot_id]
        robot_interactions = interactions_df[interactions_df['robot_id'] == robot_id]
        robot_vending = vending_df[
            (vending_df['robot_id'] == robot_id) & 
            (vending_df['payment_status'] == 'paid')
        ]
        robot_nav_events = nav_events_df[nav_events_df['robot_id'] == robot_id]
        
        # Availability: percentage of days with at least one telemetry reading
        if len(robot_telem) > 0:
            robot_telem['date'] = pd.to_datetime(robot_telem['timestamp']).dt.date
            days_with_data = len(robot_telem['date'].unique())
        else:
            days_with_data = 0
        
        availability = (days_with_data / PILOT_DAYS) * 100
        
        # Last known state
        last_state = 'unknown'
        if len(robot_telem) > 0:
            last_state = robot_telem.iloc[-1]['state']
        
        # Fault count (severity == 'warn')
        fault_count = len(robot_nav_events[robot_nav_events['severity'] == 'warn'])
        
        robot_details.append({
            'id': robot_id,
            'model': robot['model'],
            'homeZone': robot['home_zone'],
            'deployDate': robot['deploy_date'],
            'availability': round(availability, 2),
            'lastKnownState': last_state,
            'telemetryCount': len(robot_telem),
            'interactionCount': len(robot_interactions),
            'vendingRevenue': round(robot_vending['amount'].astype(float).sum(), 2),
            'navigationEventsCount': len(robot_nav_events),
            'faultCount': fault_count
        })
    
    # Per-zone metrics
    zones = {}
    for _, robot in robots_df.iterrows():
        zone = robot['home_zone']
        if zone not in zones:
            zones[zone] = {
                'zone': zone,
                'robots': [],
                'interactions': 0,
                'revenue': 0.0,
                'footfall': 0
            }
        zones[zone]['robots'].append(robot['robot_id'])
    
    # Add zone-level metrics
    for _, interaction in interactions_df.iterrows():
        robot_row = robots_df[robots_df['robot_id'] == interaction['robot_id']]
        if len(robot_row) > 0:
            zone = robot_row.iloc[0]['home_zone']
            if zone in zones:
                zones[zone]['interactions'] += 1
    
    for _, vending in vending_df.iterrows():
        if vending['payment_status'] == 'paid':
            robot_row = robots_df[robots_df['robot_id'] == vending['robot_id']]
            if len(robot_row) > 0:
                zone = robot_row.iloc[0]['home_zone']
                if zone in zones:
                    zones[zone]['revenue'] += float(vending['amount'])
    
    for _, footfall in footfall_df.iterrows():
        zone = footfall['zone']
        if zone in zones:
            zones[zone]['footfall'] += int(footfall['count'])
    
    # Round zone revenues
    for zone in zones:
        zones[zone]['revenue'] = round(zones[zone]['revenue'], 2)
    
    return {
        'summary': {
            'totalRobots': total_robots,
            'activeRobots': active_robots,
            'qrScans': total_scans,
            'qrConversions': conversions,
            'conversionRate': round(conversion_rate, 4),
            'vendingRevenue': round(total_revenue, 2),
            'vendingTransactions': transactions_counted,
            'pilotStartDate': PILOT_START.strftime('%Y-%m-%d'),
            'pilotEndDate': PILOT_END.strftime('%Y-%m-%d')
        },
        'robot_details': robot_details,
        'zone_metrics': list(zones.values()),
        'raw_metrics': {
            'definitions': {
                'availability': 'Percentage of pilot days (Jun 1-14) with at least one telemetry reading',
                'activeRobots': 'Registered robots (in robots.csv) with at least one telemetry reading in the pilot period',
                'qrConversionRate': 'Ratio of QR scans that resulted in conversion (converted=true)'
            }
        }
    }
