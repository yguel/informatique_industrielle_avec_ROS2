cmake_minimum_required(VERSION 3.16)
project(five_bars_hardware LANGUAGES CXX)

if(CMAKE_CXX_COMPILER_ID MATCHES "(GNU|Clang)")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

set(DEPS hardware_interface pluginlib rclcpp rclcpp_lifecycle realtime_tools sensor_msgs std_msgs)
find_package(ament_cmake REQUIRED)
foreach(dep ${DEPS})
  find_package(${dep} REQUIRED)
endforeach()

add_library(${PROJECT_NAME} SHARED src/mujoco_topic_system.cpp)
target_compile_features(${PROJECT_NAME} PUBLIC cxx_std_17)
target_include_directories(${PROJECT_NAME} PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include/${PROJECT_NAME}>)
target_link_libraries(${PROJECT_NAME} PUBLIC
  hardware_interface::hardware_interface
  pluginlib::pluginlib
  rclcpp::rclcpp
  rclcpp_lifecycle::rclcpp_lifecycle
  realtime_tools::realtime_tools
  ${sensor_msgs_TARGETS}
  ${std_msgs_TARGETS})

pluginlib_export_plugin_description_file(hardware_interface five_bars_hardware.xml)

install(DIRECTORY include/ DESTINATION include/${PROJECT_NAME})
install(TARGETS ${PROJECT_NAME} EXPORT export_${PROJECT_NAME}
  ARCHIVE DESTINATION lib LIBRARY DESTINATION lib RUNTIME DESTINATION bin)

ament_export_targets(export_${PROJECT_NAME} HAS_LIBRARY_TARGET)
ament_export_dependencies(${DEPS})
ament_package()
