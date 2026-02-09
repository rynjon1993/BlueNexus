"""
Data Fetcher for Lake Erie Live Monitor
Downloads latest SST and chlorophyll data from NOAA GLERL ERDDAP
Caches results in SQLite database
"""

import os
import time
import sqlite3
from datetime import datetime, timedelta
import requests
import xarray as xr
import numpy as np
import yaml
from pathlib import Path

# Load configuration
CONFIG_PATH = Path(__file__).parent / "config.yaml"
with open(CONFIG_PATH, 'r') as f:
    CONFIG = yaml.safe_load(f)

# Database path
DB_PATH = Path(__file__).parent / "cache" / "realtime_data.db"
LOG_PATH = Path(__file__).parent / "cache" / "fetch_log.txt"

# Ensure cache directory exists
DB_PATH.parent.mkdir(exist_ok=True)


def log_message(message):
    """Append message to log file with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    
    with open(LOG_PATH, 'a') as f:
        f.write(log_entry)
    
    print(log_entry.strip())


def init_database():
    """Initialize SQLite database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # SST data table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sst_data (
            date TEXT PRIMARY KEY,
            lake_mean REAL,
            lake_max REAL,
            west_basin_mean REAL,
            east_basin_mean REAL,
            data_coverage REAL,
            fetch_timestamp TEXT
        )
    """)
    
    # Chlorophyll data table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chl_data (
            date TEXT PRIMARY KEY,
            lake_mean REAL,
            lake_max REAL,
            west_basin_mean REAL,
            east_basin_mean REAL,
            data_coverage REAL,
            fetch_timestamp TEXT
        )
    """)
    
    # Bloom risk scores table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bloom_risk (
            date TEXT PRIMARY KEY,
            risk_score INTEGER,
            risk_level TEXT,
            sst_above_threshold INTEGER,
            chl_above_threshold INTEGER,
            calculation_timestamp TEXT
        )
    """)
    
    # Fetch history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fetch_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fetch_timestamp TEXT,
            data_type TEXT,
            date_range_start TEXT,
            date_range_end TEXT,
            status TEXT,
            error_message TEXT
        )
    """)
    
    conn.commit()
    conn.close()
    log_message("Database initialized successfully")


def download_erddap_data(dataset_id, variable, start_date, end_date):
    """
    Download data from NOAA GLERL ERDDAP server
    
    Args:
        dataset_id: ERDDAP dataset identifier
        variable: Variable name to download
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
    
    Returns:
        xarray.Dataset or None if download fails
    """
    bbox = CONFIG['bbox']
    erddap = CONFIG['erddap']
    
    # Time format depends on dataset
    if dataset_id == erddap['sst_dataset']:
        time_str = "T12:00:00Z"
    else:  # Chlorophyll
        time_str = "T00:00:00Z"
    
    # Build ERDDAP URL
    url = (
        f"{erddap['base_url']}/griddap/{dataset_id}.nc?"
        f"{variable}"
        f"[({start_date}{time_str}):1:({end_date}{time_str})]"
        f"[({bbox['lat_min']}):1:({bbox['lat_max']})]"
        f"[({bbox['lon_min']}):1:({bbox['lon_max']})]"
    )
    
    log_message(f"Downloading {dataset_id} from {start_date} to {end_date}...")
    
    # Use unique temp filename to avoid conflicts
    import random
    temp_suffix = random.randint(1000, 9999)
    temp_file = DB_PATH.parent / f"temp_{dataset_id}_{temp_suffix}.nc"
    
    for attempt in range(erddap['retry_attempts']):
        try:
            response = requests.get(url, timeout=120)
            response.raise_for_status()
            
            # Save to temporary file
            with open(temp_file, 'wb') as f:
                f.write(response.content)
            
            # Load with xarray
            ds = xr.open_dataset(temp_file)
            
            # IMPORTANT: Load data into memory before closing file
            ds = ds.load()
            
            # Now we can safely delete the temp file
            try:
                temp_file.unlink()
            except:
                pass  # Ignore if deletion fails
            
            log_message(f"Successfully downloaded {dataset_id}")
            return ds
            
        except Exception as e:
            log_message(f"Download attempt {attempt + 1} failed: {str(e)}")
            
            # Clean up temp file on failure
            try:
                if temp_file.exists():
                    temp_file.unlink()
            except:
                pass
            
            if attempt < erddap['retry_attempts'] - 1:
                time.sleep(erddap['retry_delay'])
            else:
                log_message(f"Failed to download {dataset_id} after {erddap['retry_attempts']} attempts")
                return None


def calculate_statistics(ds, variable):
    """
    Calculate lake-wide and basin-specific statistics
    
    Args:
        ds: xarray.Dataset
        variable: Variable name
    
    Returns:
        dict with statistics for each date
    """
    stats = {}
    western_lon = CONFIG['thresholds']['western_basin_lon']
    
    # Get coordinate names (ERDDAP uses 'latitude'/'longitude' or 'lat'/'lon')
    lat_coord = 'latitude' if 'latitude' in ds.coords else 'lat'
    lon_coord = 'longitude' if 'longitude' in ds.coords else 'lon'
    
    for date in ds.time.values:
        date_str = str(date)[:10]  # YYYY-MM-DD
        data = ds[variable].sel(time=date)
        
        # Lake-wide statistics
        lake_mean = float(data.mean(skipna=True).values)
        lake_max = float(data.max(skipna=True).values)
        data_coverage = float((~np.isnan(data.values)).sum() / data.values.size * 100)
        
        # Basin-specific statistics
        west_mask = ds[lon_coord] < western_lon
        east_mask = ds[lon_coord] >= western_lon
        
        west_data = data.where(west_mask, drop=False)
        east_data = data.where(east_mask, drop=False)
        
        west_mean = float(west_data.mean(skipna=True).values)
        east_mean = float(east_data.mean(skipna=True).values)
        
        stats[date_str] = {
            'lake_mean': lake_mean,
            'lake_max': lake_max,
            'west_basin_mean': west_mean,
            'east_basin_mean': east_mean,
            'data_coverage': data_coverage
        }
    
    return stats


def store_data(data_type, stats):
    """
    Store calculated statistics in database
    
    Args:
        data_type: 'sst' or 'chl'
        stats: Dictionary of statistics by date
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30)  # Longer timeout
        cursor = conn.cursor()
        fetch_timestamp = datetime.now().isoformat()
        
        table_name = f"{data_type}_data"
        
        for date_str, values in stats.items():
            cursor.execute(f"""
                INSERT OR REPLACE INTO {table_name}
                (date, lake_mean, lake_max, west_basin_mean, east_basin_mean, 
                 data_coverage, fetch_timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                date_str,
                values['lake_mean'],
                values['lake_max'],
                values['west_basin_mean'],
                values['east_basin_mean'],
                values['data_coverage'],
                fetch_timestamp
            ))
        
        conn.commit()
        log_message(f"Stored {len(stats)} records in {table_name}")
    
    except Exception as e:
        log_message(f"Error storing data in {table_name}: {str(e)}")
        if conn:
            conn.rollback()
    
    finally:
        if conn:
            conn.close()


def calculate_bloom_risk():
    """
    Calculate bloom risk scores based on latest SST and chlorophyll data
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get latest 7 days of data
    cursor.execute("""
        SELECT s.date, s.lake_mean as sst, c.west_basin_mean as chl
        FROM sst_data s
        LEFT JOIN chl_data c ON s.date = c.date
        ORDER BY s.date DESC
        LIMIT 7
    """)
    
    rows = cursor.fetchall()
    thresholds = CONFIG['thresholds']
    calculation_timestamp = datetime.now().isoformat()
    
    for date, sst, chl in rows:
        risk_score = 0
        sst_above = 0
        chl_above = 0
        
        # SST contribution
        if sst is not None and sst > thresholds['sst_bloom']:
            risk_score += 1
            sst_above = 1
        
        # Chlorophyll contribution
        if chl is not None:
            if chl > thresholds['chl_high']:
                risk_score += 3
                chl_above = 1
            elif chl > thresholds['chl_moderate']:
                risk_score += 2
                chl_above = 1
            elif chl > thresholds['chl_low']:
                risk_score += 1
                chl_above = 1
        
        # Determine risk level
        if risk_score >= 4:
            risk_level = "High"
        elif risk_score >= 2:
            risk_level = "Moderate"
        else:
            risk_level = "Low"
        
        # Store in database
        cursor.execute("""
            INSERT OR REPLACE INTO bloom_risk
            (date, risk_score, risk_level, sst_above_threshold, 
             chl_above_threshold, calculation_timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (date, risk_score, risk_level, sst_above, chl_above, calculation_timestamp))
    
    conn.commit()
    conn.close()
    log_message(f"Calculated bloom risk for {len(rows)} dates")


def cleanup_old_data():
    """Remove data older than retention period"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cutoff_date = (datetime.now() - timedelta(days=CONFIG['retention_days'])).strftime("%Y-%m-%d")
    
    for table in ['sst_data', 'chl_data', 'bloom_risk']:
        cursor.execute(f"DELETE FROM {table} WHERE date < ?", (cutoff_date,))
    
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    if deleted > 0:
        log_message(f"Cleaned up {deleted} old records (before {cutoff_date})")


def fetch_latest_data():
    """
    Main function - downloads latest 7 days of data and updates database
    
    NOTE: GLSEA_GCS dataset ends 2023-12-31. For live monitoring, this would use
    datetime.now(), but for historical demonstration we use the most recent 7 days
    available in the dataset (Dec 2023).
    """
    log_message("=" * 60)
    log_message("Starting data fetch...")
    
    # Initialize database if needed
    init_database()
    
    # Calculate date range - using end of 2023 (latest available data)
    # For live monitoring, change this to: datetime.now().strftime("%Y-%m-%d")
    end_date = "2023-12-31"
    start_date = "2023-12-24"  # Last 7 days of 2023
    
    erddap = CONFIG['erddap']
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Fetch SST data
    try:
        sst_ds = download_erddap_data(
            erddap['sst_dataset'],
            'sst',
            start_date,
            end_date
        )
        
        if sst_ds is not None:
            sst_stats = calculate_statistics(sst_ds, 'sst')
            store_data('sst', sst_stats)
            
            cursor.execute("""
                INSERT INTO fetch_history 
                (fetch_timestamp, data_type, date_range_start, date_range_end, status, error_message)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (datetime.now().isoformat(), 'sst', start_date, end_date, 'success', None))
            
            sst_ds.close()
        else:
            cursor.execute("""
                INSERT INTO fetch_history 
                (fetch_timestamp, data_type, date_range_start, date_range_end, status, error_message)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (datetime.now().isoformat(), 'sst', start_date, end_date, 'failed', 'Download failed'))
    
    except Exception as e:
        log_message(f"SST fetch error: {str(e)}")
        cursor.execute("""
            INSERT INTO fetch_history 
            (fetch_timestamp, data_type, date_range_start, date_range_end, status, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (datetime.now().isoformat(), 'sst', start_date, end_date, 'failed', str(e)))
    
    # Wait between requests (server throttling)
    time.sleep(erddap['request_delay'])
    
    # Fetch Chlorophyll data
    try:
        chl_ds = download_erddap_data(
            erddap['chl_dataset'],
            'Chlorophyll',
            start_date,
            end_date
        )
        
        if chl_ds is not None:
            chl_stats = calculate_statistics(chl_ds, 'Chlorophyll')
            store_data('chl', chl_stats)
            
            cursor.execute("""
                INSERT INTO fetch_history 
                (fetch_timestamp, data_type, date_range_start, date_range_end, status, error_message)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (datetime.now().isoformat(), 'chl', start_date, end_date, 'success', None))
            
            chl_ds.close()
        else:
            cursor.execute("""
                INSERT INTO fetch_history 
                (fetch_timestamp, data_type, date_range_start, date_range_end, status, error_message)
            """, (datetime.now().isoformat(), 'chl', start_date, end_date, 'failed', 'Download failed'))
    
    except Exception as e:
        log_message(f"Chlorophyll fetch error: {str(e)}")
        cursor.execute("""
            INSERT INTO fetch_history 
            (fetch_timestamp, data_type, date_range_start, date_range_end, status, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (datetime.now().isoformat(), 'chl', start_date, end_date, 'failed', str(e)))
    
    conn.commit()
    conn.close()
    
    # Calculate bloom risk scores
    calculate_bloom_risk()
    
    # Cleanup old data
    cleanup_old_data()
    
    log_message("Data fetch complete!")
    log_message("=" * 60)


if __name__ == "__main__":
    # Run standalone for testing
    fetch_latest_data()