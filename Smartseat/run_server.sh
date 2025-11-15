#!/usr/bin/env bash
# run_server.sh
# 一键管理后端服务（支持：start | stop | restart | status | logs | test | setup）
# 放在项目根（Smartseat），在 macOS + zsh 下使用。

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VENV_DIR="backend/.venv"
PYTHON="$VENV_DIR/bin/python"
UVICORN="$VENV_DIR/bin/uvicorn"
PIDFILE="backend/uvicorn.pid"
LOGFILE="backend/uvicorn.log"
PORT_DEFAULT=8000
PORT=${PORT:-$PORT_DEFAULT}

usage() {
  cat <<-EOF
Usage: $0 <command>
Commands:
  setup     Create venv and install dependencies
  start     Start the backend (creates venv if missing, runs seed)
  stop      Stop the backend if running
  restart   Stop then start
  status    Show status (pid and whether process alive)
  logs      Tail the uvicorn log
  test      Quick HTTP test: GET /api/seats

Examples:
  $0 setup
  $0 start
  $0 status
  $0 logs
  $0 test
EOF
}

ensure_venv() {
  if [ -x "$PYTHON" ]; then
    echo "使用已存在虚拟环境: $PYTHON"
    return
  fi
  echo "创建 Python 虚拟环境 -> $VENV_DIR"
  python3 -m venv "$VENV_DIR"
  echo "激活并安装依赖（这一步可能需要几分钟）"
  "$VENV_DIR/bin/python" -m pip install --upgrade pip
  "$VENV_DIR/bin/pip" install -r backend/requirements.txt
}

start_server() {
  ensure_venv
  echo "运行 seed（填充 seats，如果尚未存在）"
  "$PYTHON" -m backend.seed || true

  if [ -f "$PIDFILE" ]; then
    pid=$(cat "$PIDFILE" 2>/dev/null || echo "")
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
      echo "服务已在运行（pid=$pid）。如果要强制重启请先运行: $0 stop"
      return
    else
      echo "发现旧的 pid 文件但进程不存在，移除 pid 文件"
      rm -f "$PIDFILE"
    fi
  fi

  # 使用稳健的变量引用，避免不可见字符或未定义变量导致 set -u 报错
  LOGFILE=${LOGFILE:-backend/uvicorn.log}
  PORT=${PORT:-$PORT_DEFAULT}
  echo "启动 uvicorn，写入日志到: ${LOGFILE}，端口: ${PORT}"
  mkdir -p "$(dirname "${LOGFILE}")"
  nohup "${UVICORN}" backend.main:app --host 127.0.0.1 --port "${PORT}" --reload > "${LOGFILE}" 2>&1 &
  newpid=$!
  echo $newpid > "$PIDFILE"
  echo "已启动，PID=$newpid"
  echo "可用命令: tail -f ${LOGFILE} 或 $0 logs"
  # 健康检查
  echo "执行启动健康检查..."
  for i in {1..10}; do
    sleep 0.5
    if curl -sS "http://127.0.0.1:${PORT}/" | grep -q '"ok"'; then
      echo "健康检查通过：后端运行中 http://127.0.0.1:${PORT}/"
      return
    fi
    # 若进程已退出则提前失败
    if ! kill -0 "$newpid" 2>/dev/null; then
      echo "进程 PID $newpid 已退出，启动失败。查看日志: $LOGFILE"
      head -n 60 "$LOGFILE" || true
      echo "如日志为空，可尝试前台启动: ${UVICORN} backend.main:app --host 127.0.0.1 --port ${PORT} --reload"
      return 1
    fi
  done
  echo "健康检查未通过：未能在 5 秒内成功响应。请查看日志: $LOGFILE"
  head -n 60 "$LOGFILE" || true
}

stop_server() {
  local _PIDFILE="${PIDFILE:-backend/uvicorn.pid}"
  if [ ! -f "$_PIDFILE" ]; then
    echo "未找到 pid 文件 ($_PIDFILE)，服务可能未在运行"
    return
  fi
  pid=$(cat "$_PIDFILE" 2>/dev/null || echo "")
  if [ -z "$pid" ]; then
    echo "pid 文件为空，移除并退出"
    rm -f "$_PIDFILE"
    return
  fi
  if kill -0 "$pid" 2>/dev/null; then
    echo "停止进程 pid=$pid"
    kill "$pid"
    # 等待进程退出
    for i in {1..10}; do
      if ! kill -0 "$pid" 2>/dev/null; then
        break
      fi
      sleep 0.5
    done
    if kill -0 "$pid" 2>/dev/null; then
      echo "进程未正常退出，使用 kill -9"
      kill -9 "$pid" || true
    fi
  else
    echo "进程 pid=$pid 不存在，移除 pid 文件"
  fi
  rm -f "$_PIDFILE"
  echo "已停止"
}

status_server() {
  local _PIDFILE="${PIDFILE:-backend/uvicorn.pid}"
  if [ -f "$_PIDFILE" ]; then
    pid=$(cat "$_PIDFILE" 2>/dev/null || echo "")
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
      echo "服务运行中，PID=$pid"
    else
      echo "pid 文件存在但进程未运行 (pid=$pid)"
    fi
  else
    echo "服务未运行（找不到 $_PIDFILE）"
  fi
}

logs() {
  local _LOGFILE="${LOGFILE:-backend/uvicorn.log}"
  if [ ! -f "$_LOGFILE" ]; then
    echo "日志文件不存在: $_LOGFILE"
    return
  fi
  tail -n 200 -f "$_LOGFILE"
}

http_test() {
  echo "HTTP 测试: GET /api/seats -> http://127.0.0.1:$PORT/api/seats"
  if command -v jq >/dev/null 2>&1; then
    curl -sS "http://127.0.0.1:$PORT/api/seats" | jq .
  else
    curl -sS "http://127.0.0.1:$PORT/api/seats" || true
  fi
}

case ${1-} in
  setup)
    ensure_venv
    ;;
  start)
    start_server
    ;;
  stop)
    stop_server
    ;;
  restart)
    stop_server || true
    start_server
    ;;
  reset)
    echo "[RESET] Stopping server..."
    stop_server || true
    echo "[RESET] Backing up DB if exists..."
    DB_FILE="backend/../app.db"
    DB_PATH="$(cd "$(dirname "$DB_FILE")" && pwd)/$(basename "$DB_FILE")"
    if [ -f "$DB_PATH" ]; then
      BK="${DB_PATH}.bak.$(date +%Y%m%d%H%M%S)"
      mv "$DB_PATH" "$BK"
      echo "[RESET] Moved $DB_PATH -> $BK"
    else
      echo "[RESET] No existing DB at $DB_PATH"
    fi
    echo "[RESET] Ensuring venv and seeding fresh DB..."
    ensure_venv
    "$PYTHON" - <<'PY'
from backend.database import Base, engine
Base.metadata.create_all(bind=engine)
print("created tables")
PY
    "$PYTHON" -m backend.seed || true
    echo "[RESET] Starting server..."
    start_server
    ;;
  status)
    status_server
    ;;
  logs)
    logs
    ;;
  test)
    http_test
    ;;
  *)
    usage
    exit 1
    ;;
esac
