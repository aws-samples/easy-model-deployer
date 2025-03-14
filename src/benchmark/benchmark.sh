export BASE_URL=http://localhost:8080
export SYSTEM_PROMPT=1
export MAX_TOKENS=2048
export MIN_TOKENS=0
python benchmark.py --max_users 1 --session_time 300 --ping_correction
