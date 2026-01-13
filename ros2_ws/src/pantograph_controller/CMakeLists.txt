cmake_minimum_required(VERSION 3.8)
project(pantograph_controller)

# Default to C++17
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(controller_interface REQUIRED)
find_package(pluginlib REQUIRED)
find_package(hardware_interface REQUIRED)
find_package(realtime_tools REQUIRED)
find_package(rclcpp_lifecycle REQUIRED)

include_directories(include)

add_library(${PROJECT_NAME} SHARED
  src/pantograph_controller.cpp
)

ament_target_dependencies(${PROJECT_NAME}
  rclcpp
  controller_interface
  pluginlib
  hardware_interface
  realtime_tools
  rclcpp_lifecycle
)

target_include_directories(${PROJECT_NAME} PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)

# Export controller plugin
pluginlib_export_plugin_description_file(
  controller_interface
  pantograph_controller_plugins.xml
)

install(
  TARGETS ${PROJECT_NAME}
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
)

install(
  DIRECTORY include/
  DESTINATION include
)

ament_package()
