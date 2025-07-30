# 🎌 UkiyoFusion Startup Scripts

This directory contains several scripts to easily run your UkiyoFusion application:

## 📁 Available Scripts

### 🚀 `start_simple.sh` (Recommended)

**Quick and easy startup script**

```bash
./start_simple.sh
```

- Starts both backend and frontend servers
- Shows output directly in terminal
- Automatic cleanup on Ctrl+C
- Process monitoring and error handling

### 🔧 `run_ukiyoe.sh` (Advanced)

**Full-featured startup script with logging**

```bash
./run_ukiyoe.sh
```

- Starts both servers with detailed logging
- Logs saved to `logs/backend.log` and `logs/frontend.log`
- Advanced process management
- Status monitoring and automatic restart detection

### 🛑 `stop_servers.sh`

**Stop all running servers**

```bash
./stop_servers.sh
```

- Cleanly stops both backend and frontend
- Kills any processes on ports 5001 and 8081
- Use this if servers don't stop properly

## 🌐 Access URLs

Once started, access your application at:

- **Frontend (Web UI):** http://localhost:8081
- **Backend (API):** http://localhost:5001

## 🎨 Features

Your UkiyoFusion application includes:

- ✅ Custom ukiyo-e diffusers model
- ✅ Optimized parameters for authentic Edo-period style
- ✅ Negative prompting to avoid modern elements
- ✅ Multiple style presets
- ✅ Real-time transformation progress

## 🔍 Troubleshooting

**If servers won't start:**

1. Run `./stop_servers.sh` first
2. Check that you're in the UkiyoFusion directory
3. Verify the virtual environment exists at `backend/simple_venv/`

**If you see "Address already in use":**

- Run `./stop_servers.sh` to kill existing processes
- Wait a few seconds and try again

**For detailed debugging:**

- Use `run_ukiyoe.sh` and check the log files in `logs/`

## 📝 Manual Commands

If you prefer to run manually:

**Backend:**

```bash
cd backend
./simple_venv/bin/python simple_app.py
```

**Frontend:**

```bash
cd simple_frontend
python3 -m http.server 8081
```

---

🎌 **Enjoy creating beautiful ukiyo-e transformations!**
