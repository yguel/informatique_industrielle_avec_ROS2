#!/usr/bin/env bash
# Build the Docker image (if needed) and open a shell in the five-bar container.
#
# Can be called from anywhere (paths are resolved from this script's location):
#   docker/start.sh            build the image if missing, then open an interactive shell
#   docker/start.sh --rebuild  force a rebuild of the image, then open a shell
#   docker/start.sh test       run all unit tests headless (same as the GitHub CI)
#   docker/start.sh <cmd...>   run any command in the container, e.g. docker/start.sh ros2 run five_bars_mujoco direct_gui
#
# Layout: this script and docker-compose.yml live in docker/, the sources in ../src.
# The build context is the repository root (the image copies src/ into /ws/src).
#
# Your ../src folder is mounted in the container (/ws/src): edit on the host, then run
# `colcon build` in the container. The workspace is rebuilt automatically at startup.
set -euo pipefail

IMAGE="five_bars:dev"
CONTAINER="five_bars_dev"
DOCKER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"   # .../five_bars_ws/docker
ROOT="$(cd "$DOCKER_DIR/.." && pwd)"                          # .../five_bars_ws (build context)
SRC_DIR="$ROOT/src"

if [[ ! -d "$SRC_DIR" ]]; then
  echo "Error: sources not found in $SRC_DIR (expected layout: docker/ and src/ side by side)." >&2
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "Error: docker is not installed (https://docs.docker.com/engine/install/)." >&2
  exit 1
fi

# ---------------------------------------------------------------- build the image
REBUILD=0
if [[ "${1:-}" == "--rebuild" ]]; then
  REBUILD=1
  shift
fi
if [[ $REBUILD -eq 1 ]] || ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  echo ">>> Building image $IMAGE (first time: ~10 min)..."
  docker build -f "$DOCKER_DIR/Dockerfile" --target desktop -t "$IMAGE" "$ROOT"
fi

# ------------------------------------------------------------ what to run inside
BUILD_CMD="colcon build --event-handlers console_cohesion- --cmake-args -DCMAKE_BUILD_TYPE=RelWithDebInfo > /tmp/colcon_build.log 2>&1 \
  || { cat /tmp/colcon_build.log; echo '!!! colcon build failed'; }; source /ws/install/setup.bash"

if [[ $# -eq 0 ]]; then
  INNER="$BUILD_CMD; echo '>>> Workspace built. Try: ros2 run five_bars_mujoco direct_gui'; exec bash"
elif [[ "$1" == "test" ]]; then
  INNER="$BUILD_CMD; colcon test --event-handlers console_direct+; colcon test-result --verbose"
else
  INNER="$BUILD_CMD; exec $(printf '%q ' "$@")"
fi

# --------------------------------------------------- display (X11) and GPU options
DOCKER_ARGS=(--rm -it --name "$CONTAINER" --network host --ipc host
             -v "$SRC_DIR:/ws/src"
             -e "ROS_DOMAIN_ID=${ROS_DOMAIN_ID:-0}")

if [[ -n "${DISPLAY:-}" ]]; then
  # Allow local containers to open windows on your X server (Linux, also XWayland).
  if command -v xhost >/dev/null 2>&1; then
    xhost +local:docker >/dev/null 2>&1 || true
  fi
  DOCKER_ARGS+=(-e "DISPLAY=$DISPLAY" -e QT_X11_NO_MITSHM=1 -v /tmp/.X11-unix:/tmp/.X11-unix:rw)
else
  echo ">>> No DISPLAY: GUIs (MuJoCo viewer, sliders, RViz) will not open; headless use only."
fi
if [[ -e /dev/dri ]]; then
  DOCKER_ARGS+=(--device /dev/dri)   # GPU acceleration for the viewer (Intel/AMD)
fi

# A second docker/start.sh opens a new shell in the container that is already running.
if docker ps --format '{{.Names}}' | grep -qx "$CONTAINER"; then
  echo ">>> Container $CONTAINER is already running: opening another shell in it."
  exec docker exec -it "$CONTAINER" bash -c \
    'source /opt/ros/$ROS_DISTRO/setup.bash && source /ws/install/setup.bash && exec bash'
fi

exec docker run "${DOCKER_ARGS[@]}" "$IMAGE" bash -c "$INNER"
