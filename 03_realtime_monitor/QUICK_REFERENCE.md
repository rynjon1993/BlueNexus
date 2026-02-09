# Phase 6 Quick Reference Card

**⚓ Lake Erie Live Monitor — Essential Commands**

---

## 🚀 First-Time Setup (5 minutes)

```bash
# 1. Navigate to project
cd E:\BlueNexus\03_realtime_monitor

# 2. Activate environment
E:\BlueNexus\ocean_env\Scripts\activate

# 3. Install dependencies
pip install streamlit apscheduler pyyaml

# 4. Initialize data
python data_fetcher.py

# 5. Launch dashboard
streamlit run app.py
```

---

## 🎯 Daily Operations

### Launch Dashboard
```bash
cd E:\BlueNexus\03_realtime_monitor
E:\BlueNexus\ocean_env\Scripts\activate
streamlit run app.py
```
Opens at: **http://localhost:8501**

### Manual Data Refresh
Click **"Refresh Now"** button in dashboard sidebar  
*Or run standalone:*
```bash
python data_fetcher.py
```

### Check Status
- **Dashboard:** System Status tab → Fetch History
- **Logs:** `cache\fetch_log.txt`
- **Database:** `cache\realtime_data.db`

---

## 🔧 Maintenance Commands

### Test Components
```bash
# Test data fetcher
python data_fetcher.py

# Test alert engine
python alert_engine.py

# Test utilities
python utils.py
```

### Clean Cache
```bash
# Delete all cached data (will re-download on next run)
rmdir /S cache
```

### View Database
```bash
sqlite3 cache\realtime_data.db
.tables
SELECT COUNT(*) FROM sst_data;
SELECT COUNT(*) FROM chl_data;
.quit
```

### Update Dependencies
```bash
pip install --upgrade streamlit apscheduler pyyaml
```

---

## 🛠️ Configuration Quick Edits

**File:** `config.yaml`

### Change Update Time
```yaml
schedule:
  hour: 8        # 0-23 (24-hour format)
  minute: 0
```

### Adjust Bloom Thresholds
```yaml
thresholds:
  sst_bloom: 20.0              # °C
  chl_moderate: 20.0           # mg/m³
```

---

## 🚨 Troubleshooting One-Liners

### Dashboard won't start
```bash
pip install streamlit apscheduler pyyaml
```

### No data showing
```bash
python data_fetcher.py
```

### Download errors (502, timeout)
```
Wait 10 minutes, then click "Refresh Now" in dashboard
```

### Scheduler not updating
```
Keep dashboard open, or use Windows Task Scheduler (see SETUP.md)
```

---

## 📊 File Locations

| File | Path | Purpose |
|------|------|---------|
| **Dashboard** | `E:\BlueNexus\03_realtime_monitor\app.py` | Main application |
| **Config** | `E:\BlueNexus\03_realtime_monitor\config.yaml` | Settings |
| **Database** | `E:\BlueNexus\03_realtime_monitor\cache\realtime_data.db` | Cached data |
| **Logs** | `E:\BlueNexus\03_realtime_monitor\cache\fetch_log.txt` | Error logs |

---

## 🎓 Key Concepts

**Data Flow:**
```
NOAA ERDDAP → data_fetcher.py → SQLite → Dashboard
```

**Update Schedule:**
```
APScheduler → Runs daily at 8 AM → Fetches 7 days → Updates database
```

**Bloom Risk Scoring:**
```
SST > 20°C = +1 point
Chl 10-20 mg/m³ = +1 point
Chl 20-40 mg/m³ = +2 points
Chl > 40 mg/m³ = +3 points

0-1 = Low (🟢)
2-3 = Moderate (🟡)
4+ = High (🔴)
```

---

## 🌐 URLs

| Service | URL |
|---------|-----|
| **Dashboard** | http://localhost:8501 |
| **NOAA ERDDAP** | https://apps.glerl.noaa.gov/erddap |
| **GitHub Repo** | https://github.com/rynjon1993/BlueNexus |

---

## 📦 Dependencies

```
streamlit      >= 1.31.0
apscheduler    >= 3.10.0
pyyaml         >= 6.0
xarray         >= 2023.6.0
cartopy        >= 0.22.0
matplotlib     >= 3.7.0
```

---

## Git Commands

```bash
# Add Phase 6 files
git add 03_realtime_monitor/

# Commit
git commit -m "feat: Phase 6 real-time dashboard"

# Push
git push origin main
```

---

**⚓ Keep this card handy for quick reference during operations!**
