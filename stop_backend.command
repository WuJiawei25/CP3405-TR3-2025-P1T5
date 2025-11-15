#!/bin/bash
# macOS 一键停止后端（双击可运行，或在终端执行 ./stop_backend.command）
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="$ROOT_DIR/backend_stop.log"
{
  echo "========================================"
  echo "[STOP ] $(date '+%F %T')"
  echo "PWD: $ROOT_DIR"
  echo "USER: $(whoami)"
  echo "BASH: $BASH_VERSION"
} >> "$LOG_FILE" 2>&1
exec > >(tee -a "$LOG_FILE") 2>&1

trap 'code=$?; echo; echo "[ERROR] 停止过程中发生错误 (code=$code)。上方输出与 $LOG_FILE 可用于排查。"; if [[ -z "${SSH_TTY:-}" ]]; then read -r -p "按回车关闭窗口..." _; fi; exit $code' ERR

cd "$ROOT_DIR" || exit 1
if [ ! -d "Smartseat" ]; then
  echo "[FATAL] 未找到 Smartseat 目录，请确认脚本位于项目根 (P1T5) 下。"
  if [[ -z "${SSH_TTY:-}" ]]; then read -r -p "按回车退出..." _; fi
  exit 1
fi

cd Smartseat
chmod +x run_server.sh || true

echo "[STEP] 停止后端服务 (stop)"
bash ./run_server.sh stop || true

echo "[STEP] 查询服务状态 (status)"
bash ./run_server.sh status || true

echo "----------------------------------------"
echo "后端已尝试停止。"
echo "- 查看日志：  Smartseat/backend/uvicorn.log (或执行: bash Smartseat/run_server.sh logs)"
echo "- 再次启动：  ./start_backend.command 或 bash Smartseat/run_server.sh start"
echo "本次停止输出也已保存到: $LOG_FILE"
echo "----------------------------------------"

if [[ -z "${SSH_TTY:-}" ]]; then
  read -r -p "按回车关闭此窗口..." _
fi
