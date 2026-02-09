# Lake Erie Live Monitor - Setup Guide

Complete setup instructions for running the real-time monitoring dashboard.

---

## Prerequisites

- Python 3.10 or higher
- Virtual environment activated (`ocean_env`)
- Internet connection (for NOAA ERDDAP data)

---

## Installation Steps

### 1. Navigate to Project Directory

```bash
cd E:\BlueNexus\03_realtime_monitor
```

### 2. Activate Virtual Environment

```bash
E:\BlueNexus\ocean_env\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install streamlit apscheduler pyyaml
```

Verify installation:
```bash
pip list | findstr /I "streamlit apscheduler yaml"
```

Expected output:
```
apscheduler      3.10.4
PyYAML           6.0.1
streamlit        1.31.1
```

### 4. Verify File Structure

Ensure all files are in place:

```
03_realtime_monitor/
├── README.md
├── SETUP.md                    ← You are here
├── app.py                      ← Main dashboard
├── data_fetcher.py             ← Data pipeline
├── alert_engine.py             ← Risk scoring
├── utils.py                    ← Plotting functions
├── config.yaml                 ← Configuration
├── .gitignore
└── cache/                      ← Will be created automatically
```

---

## First Run

### Test Data Fetcher (Standalone)

Before running the full dashboard, test the data fetcher independently:

```bash
python data_fetcher.py
```

**Expected output:**
```
[2026-02-08 14:30:00] ====================================================
[2026-02-08 14:30:00] Starting data fetch...
[2026-02-08 14:30:00] Database initialized successfully
[2026-02-08 14:30:05] Downloading GLSEA_GCS from 2026-02-01 to 2026-02-08...
[2026-02-08 14:30:25] Successfully downloaded GLSEA_GCS
[2026-02-08 14:30:25] Stored 7 records in sst_data
[2026-02-08 14:30:45] Downloading LE_CHL_VIIRS_SQ from 2026-02-01 to 2026-02-08...
[2026-02-08 14:31:05] Successfully downloaded LE_CHL_VIIRS_SQ
[2026-02-08 14:31:05] Stored 7 records in chl_data
[2026-02-08 14:31:05] Calculated bloom risk for 7 dates
[2026-02-08 14:31:05] Data fetch complete!
[2026-02-08 14:31:05] ====================================================
```

**If this succeeds:**
- SQLite database created at `cache/realtime_data.db`
- 7 days of SST and chlorophyll data downloaded
- Bloom risk scores calculated
- Ready to launch dashboard

**If this fails:**
- Check internet connection
- Verify NOAA ERDDAP server is accessible: https://apps.glerl.noaa.gov/erddap
- Check `cache/fetch_log.txt` for error details

---

## Launch Dashboard

```bash
streamlit run app.py
```

**Expected behavior:**
1. Terminal shows: `You can now view your Streamlit app in your browser.`
2. Browser opens automatically to `http://localhost:8501`
3. Dashboard loads with "Initialize Data" button (if first run after cache clear)

**If data was pre-fetched (from standalone test):**
- Dashboard loads immediately with current conditions
- Sidebar shows bloom risk status
- APScheduler starts background job for daily updates

---

## Dashboard Navigation

### Sidebar
- **Refresh Now** — Manually trigger data fetch
- **Bloom Risk** — Current risk level and score
- **Data Status** — Last update time and freshness
- **Current Metrics** — Lake-wide SST, chlorophyll, days above threshold

### Main Tabs
1. **Overview** — Current conditions summary, 7-day statistics
2. **Trends** — Time series charts, daily risk history
3. **Historical Data** — Tabular view of SST and chlorophyll records
4. **System Status** — Fetch history, configuration, about section

---

## Configuration

Edit `config.yaml` to customize:

### Update Schedule
```yaml
schedule:
  hour: 8        # Default: 8:00 AM
  minute: 0
  timezone: "America/New_York"
```

### Bloom Risk Thresholds
```yaml
thresholds:
  sst_bloom: 20.0              # °C
  chl_low: 10.0                # mg/m³
  chl_moderate: 20.0           # mg/m³
  chl_high: 40.0               # mg/m³
```

### Data Retention
```yaml
retention_days: 30             # Keep 30 days of historical data
```

---

## Automated Updates

The dashboard includes **APScheduler** for background data fetching:

- **Default schedule:** Daily at 8:00 AM EST
- **Runs automatically** while the dashboard is open
- **Manual trigger:** Click "Refresh Now" in sidebar

**Important:** APScheduler only runs while the Streamlit app is active. For 24/7 monitoring:

### Option 1: Keep Dashboard Running (Local)
Leave the terminal and browser open. Dashboard will fetch data at 8 AM daily.

### Option 2: Windows Task Scheduler (Headless)
Create a separate scheduled task that runs `python data_fetcher.py` daily at 8 AM:

```bash
# Create Windows Task Scheduler entry (run as Administrator)
schtasks /create /tn "Lake Erie Data Fetch" /tr "E:\BlueNexus\ocean_env\Scripts\python.exe E:\BlueNexus\03_realtime_monitor\data_fetcher.py" /sc daily /st 08:00
```

Then access the dashboard anytime — data will always be current.

### Option 3: Cloud Deployment (Future)
Deploy to Streamlit Cloud with GitHub Actions for scheduled fetching (see README for details).

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'streamlit'"

**Solution:**
```bash
# Ensure virtual environment is activated
E:\BlueNexus\ocean_env\Scripts\activate

# Reinstall dependencies
pip install streamlit apscheduler pyyaml
```

---

### Issue: "Error loading data: no such table: sst_data"

**Cause:** Database not initialized

**Solution:**
```bash
# Run data fetcher standalone to initialize database
python data_fetcher.py
```

---

### Issue: "Download failed" or "502 Bad Gateway"

**Cause:** NOAA ERDDAP server throttling or temporary outage

**Solution:**
- Wait 5-10 minutes and click "Refresh Now"
- Check ERDDAP server status: https://apps.glerl.noaa.gov/erddap
- Check `cache/fetch_log.txt` for specific error messages

---

### Issue: Dashboard shows "No data" after initialization

**Cause:** Data fetch may have partially succeeded

**Solution:**
```bash
# Check database manually
sqlite3 cache/realtime_data.db
sqlite> SELECT COUNT(*) FROM sst_data;
sqlite> SELECT COUNT(*) FROM chl_data;
sqlite> .quit

# If tables are empty, run fetcher again
python data_fetcher.py
```

---

### Issue: Scheduler not running daily updates

**Cause:** Dashboard closed before 8 AM or APScheduler issue

**Solution:**
- Keep dashboard open in background
- Or use Windows Task Scheduler for headless operation (see Option 2 above)
- Check "System Status" tab → Fetch History to verify last update time

---

## Testing Checklist

Before pushing to GitHub, verify:

- [ ] `python data_fetcher.py` runs successfully
- [ ] `python alert_engine.py` shows current risk assessment
- [ ] `python utils.py` runs without errors
- [ ] `streamlit run app.py` launches dashboard at localhost:8501
- [ ] "Initialize Data" button downloads data (if cache empty)
- [ ] "Refresh Now" button triggers new data fetch
- [ ] All four tabs load without errors
- [ ] Sidebar shows bloom risk and metrics
- [ ] Time series plot displays correctly
- [ ] SQLite database created at `cache/realtime_data.db`
- [ ] Log file created at `cache/fetch_log.txt`

---

## Next Steps

### 1. Add to GitHub

```bash
cd E:\BlueNexus
git add 03_realtime_monitor/
git commit -m "feat: add Phase 6 real-time monitoring dashboard"
git push origin main
```

### 2. Update Master README

Update the projects table to mark Phase 6 as complete.

### 3. Optional Enhancements

- Add email/SMS alerts for high bloom risk
- Implement historical playback slider
- Export daily summaries as PDF reports
- Deploy to Streamlit Cloud for public access

---

## Support

For issues or questions:
- Check `cache/fetch_log.txt` for detailed error logs
- Review configuration in `config.yaml`
- Consult NOAA ERDDAP documentation: https://apps.glerl.noaa.gov/erddap
- Refer to Project Blue Nexus main repository: https://github.com/rynjon1993/BlueNexus

---

**Part of Project Blue Nexus** — Real-time oceanographic monitoring for the Great Lakes
