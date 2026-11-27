#!/bin/bash
set -e
source "/opt/ros/${ROS_DISTRO}/setup.bash"
if [ -f /ws/install/setup.bash ]; then
  source /ws/install/setup.bash
fi
# Raccourcis du cours (ros2_build, ros2_test, fb_gui ...). Les alias ne sont pas
# hérités par un shell non interactif : on les expose quand même ici pour que
# `docker/start.sh fb_test` fonctionne.
if [ -f /etc/ros2_aliases.bash ]; then
  shopt -s expand_aliases
  source /etc/ros2_aliases.bash
fi
exec "$@"
