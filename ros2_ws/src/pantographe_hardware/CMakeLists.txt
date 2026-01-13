cmake_minimum_required(VERSION 3.8)
project(pantographe_hardware)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_lifecycle REQUIRED)
find_package(hardware_interface REQUIRED)
find_package(pluginlib REQUIRED)
find_package(dynamixel_sdk REQUIRED)

add_library(
  pantographe_hardware
  SHARED
  src/pantographe_hardware_interface.cpp
)

target_include_directories(pantographe_hardware PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)

ament_target_dependencies(pantographe_hardware
  rclcpp
  rclcpp_lifecycle
  hardware_interface
  pluginlib
  dynamixel_sdk
)

pluginlib_export_plugin_description_file(hardware_interface pantographe_hardware_interface.xml)

install(
  TARGETS pantographe_hardware
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
)

install(DIRECTORY include/
  DESTINATION include
)

ament_export_include_directories(include)
ament_export_libraries(pantographe_hardware)
ament_export_dependencies(
  hardware_interface
  pluginlib
  rclcpp
  rclcpp_lifecycle
)

ament_package()
