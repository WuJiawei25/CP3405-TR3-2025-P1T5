#!/bin/bash
# macOS 一键启动后端（双击可运行，或在终端执行 ./start_backend.command）
set -euo pipefail

# 记录日志到项目根目录，便于排查
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="$ROOT_DIR/backend_start.log"
{
  echo "========================================"
  echo "[START] $(date '+%F %T')"
  echo "PWD: $ROOT_DIR"
  echo "USER: $(whoami)"
  echo "BASH: $BASH_VERSION"
} >> "$LOG_FILE" 2>&1
exec > >(tee -a "$LOG_FILE") 2>&1

trap 'code=$?; echo; echo "[ERROR] 启动过程中发生错误 (code=$code)。上方输出与 $LOG_FILE 可用于排查。"; if [[ -z "${SSH_TTY:-}" ]]; then read -r -p "按回车关闭窗口..." _; fi; exit $code' ERR

cd "$ROOT_DIR" || exit 1
if [ ! -d "Smartseat" ]; then
  echo "[FATAL] 未找到 Smartseat 目录，请确认脚本位于项目根 (P1T5) 下。"
  if [[ -z "${SSH_TTY:-}" ]]; then read -r -p "按回车退出..." _; fi
  exit 1
fi

cd Smartseat
chmod +x run_server.sh || true

# 显示准备信息
echo "[INFO] 使用脚本: $(pwd)/run_server.sh"
command -v python3 >/dev/null 2>&1 || { echo "[WARN] 未找到 python3，脚本会尝试使用系统 Python。"; }

# 初始化依赖（若已安装会快速跳过）
echo "[STEP] 安装依赖与初始化虚拟环境 (setup)"
bash ./run_server.sh setup

# 启动（包含建表与 seed）
echo "[STEP] 启动后端服务 (start)"
bash ./run_server.sh start

# 显示状态
echo "[STEP] 查询服务状态 (status)"
bash ./run_server.sh status || true

# 健康检查
PORT=${PORT:-8000}
echo "[STEP] 健康检查: GET / 与 GET /api/seats (PORT=$PORT)"
if command -v curl >/dev/null 2>&1; then
  echo "- / ->"
  curl -sS "http://127.0.0.1:${PORT}/" | head -c 400 || true; echo
  echo "- /api/seats ->"
  curl -sS "http://127.0.0.1:${PORT}/api/seats" | head -c 400 || true; echo
else
  echo "[WARN] 系统缺少 curl，跳过健康检查。"
fi

echo "----------------------------------------"
echo "后端已尝试启动。"
echo "- 查看日志：  Smartseat/backend/uvicorn.log (或执行: bash Smartseat/run_server.sh logs)"
echo "- 快速测试：  bash Smartseat/run_server.sh test"
echo "- 停止服务：  ./stop_backend.command 或 bash Smartseat/run_server.sh stop"
echo "默认访问地址：http://127.0.0.1:${PORT}/"
echo "本次启动输出也已保存到: $LOG_FILE"
echo "----------------------------------------"

# 若通过 Finder 双击运行，避免窗口秒关
if [[ -z "${SSH_TTY:-}" ]]; then
  read -r -p "按回车关闭此窗口（服务仍在后台运行）..." _
fi
