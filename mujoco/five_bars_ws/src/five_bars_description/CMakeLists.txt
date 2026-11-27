cmake_minimum_required(VERSION 3.16)
project(five_bars_description)

find_package(ament_cmake REQUIRED)

install(DIRECTORY config meshes mjcf urdf tools
  DESTINATION share/${PROJECT_NAME})

ament_package()
