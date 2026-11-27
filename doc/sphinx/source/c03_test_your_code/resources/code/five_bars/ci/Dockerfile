# Image ROS 2 Jazzy + MuJoCo (Python ET C) + Google Test + système 5 barres.
#
# Build context = repository root (the image copies src/). From the repository root:
#   docker build -f docker/Dockerfile --target ci      -t five_bars:ci .   # headless (CI, tests)
#   docker build -f docker/Dockerfile --target desktop -t five_bars:dev .  # + RViz, GUI (X11)
# or simply: docker/start.sh   /   docker compose -f docker/docker-compose.yml build
#
# La bibliothèque C de MuJoCo utilisée par les tests gtest est celle livrée dans la roue
# pip `mujoco` (include/ + libmujoco.so.X.Y.Z) : Python et C++ utilisent EXACTEMENT la
# même version de MuJoCo. Pour utiliser une archive officielle à la place, définir MUJOCO_DIR.

ARG ROS_DISTRO=jazzy

# ----------------------------------------------------------------------------- base
FROM ros:${ROS_DISTRO}-ros-base AS base
ARG ROS_DISTRO
ARG MUJOCO_VERSION=4.0.1
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential cmake git python3-pip python3-numpy python3-yaml python3-pytest python3-tk \
      googletest libgtest-dev libgmock-dev \
      ros-${ROS_DISTRO}-ament-cmake-gtest \
      ros-${ROS_DISTRO}-ament-cmake-pytest \
      ros-${ROS_DISTRO}-ros2-control \
      ros-${ROS_DISTRO}-ros2-controllers \
      ros-${ROS_DISTRO}-xacro \
      ros-${ROS_DISTRO}-robot-state-publisher \
      ros-${ROS_DISTRO}-tf2-ros-py \
      libgl1 libegl1 libglfw3 libosmesa6 \
    && rm -rf /var/lib/apt/lists/*

# MuJoCo (Python + bibliothèque C embarquée dans la roue)
RUN pip3 install --no-cache-dir --break-system-packages "mujoco==${MUJOCO_VERSION}" \
 && MJ="$(python3 -c 'import mujoco, os; print(os.path.dirname(mujoco.__file__))')" \
 && ln -s "${MJ}" /opt/mujoco \
 && echo "${MJ}" > /etc/ld.so.conf.d/mujoco.conf && ldconfig \
 && python3 -c "import mujoco; print('MuJoCo', mujoco.__version__)" \
 && ls /opt/mujoco/include/mujoco/mujoco.h /opt/mujoco/libmujoco.so*
ENV MUJOCO_DIR=/opt/mujoco

WORKDIR /ws
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]

# ------------------------------------------------------------------------------- ci
# Workspace compilé, prêt pour `colcon test` (tout est headless).
FROM base AS ci
COPY src /ws/src
RUN . /opt/ros/${ROS_DISTRO}/setup.sh \
 && colcon build --event-handlers console_direct+ --cmake-args -DCMAKE_BUILD_TYPE=RelWithDebInfo

# -------------------------------------------------------------------------- desktop
# Pour le développement : RViz, outils graphiques et conversion CAO (trimesh).
FROM ci AS desktop
RUN apt-get update && apt-get install -y --no-install-recommends \
      ros-${ROS_DISTRO}-rviz2 ros-${ROS_DISTRO}-rqt-graph ros-${ROS_DISTRO}-rqt-plot \
      mesa-utils xvfb \
    && rm -rf /var/lib/apt/lists/* \
 && pip3 install --no-cache-dir --break-system-packages trimesh pycollada fast_simplification
