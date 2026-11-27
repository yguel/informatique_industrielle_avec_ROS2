cmake_minimum_required(VERSION 3.16)
project(five_bars_kinematics LANGUAGES CXX)

if(CMAKE_CXX_COMPILER_ID MATCHES "(GNU|Clang)")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)

# --- Bibliothèque C++ : modèles géométriques direct / inverse (à implémenter) ---
add_library(${PROJECT_NAME} SHARED src/kinematics.cpp)
target_compile_features(${PROJECT_NAME} PUBLIC cxx_std_17)
target_include_directories(${PROJECT_NAME} PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include/${PROJECT_NAME}>)

install(DIRECTORY include/ DESTINATION include/${PROJECT_NAME})
install(TARGETS ${PROJECT_NAME} EXPORT export_${PROJECT_NAME}
  ARCHIVE DESTINATION lib LIBRARY DESTINATION lib RUNTIME DESTINATION bin)
ament_export_targets(export_${PROJECT_NAME} HAS_LIBRARY_TARGET)

# --- Module Python équivalent ---
ament_python_install_package(${PROJECT_NAME})

# --- Tests : vérité terrain = simulation MuJoCo headless ---
if(BUILD_TESTING)
  find_package(ament_cmake_gtest REQUIRED)
  find_package(ament_cmake_pytest REQUIRED)
  find_package(five_bars_description REQUIRED)

  list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
  find_package(MuJoCo REQUIRED)
  message(STATUS "MuJoCo : ${MuJoCo_LIBRARY} (version ${MuJoCo_VERSION})")

  # share/five_bars_description/cmake/.. -> share/five_bars_description
  get_filename_component(_desc_share "${five_bars_description_DIR}/.." ABSOLUTE)
  set(FIVE_BARS_MJCF "${_desc_share}/mjcf/five_bars.xml")

  ament_add_gtest(test_kinematics_cpp test/test_kinematics.cpp TIMEOUT 300)
  target_link_libraries(test_kinematics_cpp ${PROJECT_NAME} MuJoCo::MuJoCo)
  target_compile_definitions(test_kinematics_cpp PRIVATE FIVE_BARS_MJCF_PATH="${FIVE_BARS_MJCF}")

  ament_add_pytest_test(test_kinematics_py test/test_kinematics.py
    TIMEOUT 300
    ENV FIVE_BARS_MJCF=${FIVE_BARS_MJCF})
endif()

ament_package()
