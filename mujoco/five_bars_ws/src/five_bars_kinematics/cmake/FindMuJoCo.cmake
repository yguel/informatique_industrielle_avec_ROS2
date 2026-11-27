# FindMuJoCo.cmake — trouve la bibliothèque C de MuJoCo et crée la cible MuJoCo::MuJoCo.
#
# Ordre de recherche :
#   1. variable CMake / d'environnement MUJOCO_DIR (archive officielle :
#      https://github.com/google-deepmind/mujoco/releases -> include/ et lib/) ;
#   2. la roue Python `mujoco` (pip install mujoco) qui embarque include/ et libmujoco.so.X.Y.Z :
#      garantit la MÊME version de MuJoCo en Python et en C++.
#
# Variables définies : MuJoCo_FOUND, MuJoCo_INCLUDE_DIR, MuJoCo_LIBRARY, MuJoCo_VERSION

set(_mujoco_hints "")
if(DEFINED MUJOCO_DIR)
  list(APPEND _mujoco_hints "${MUJOCO_DIR}")
endif()
if(DEFINED ENV{MUJOCO_DIR})
  list(APPEND _mujoco_hints "$ENV{MUJOCO_DIR}")
endif()

find_package(Python3 COMPONENTS Interpreter QUIET)
if(Python3_Interpreter_FOUND)
  execute_process(
    COMMAND ${Python3_EXECUTABLE} -c "import mujoco, os; print(os.path.dirname(mujoco.__file__))"
    OUTPUT_VARIABLE _mujoco_py_dir OUTPUT_STRIP_TRAILING_WHITESPACE ERROR_QUIET
    RESULT_VARIABLE _mujoco_py_res)
  if(_mujoco_py_res EQUAL 0 AND EXISTS "${_mujoco_py_dir}")
    list(APPEND _mujoco_hints "${_mujoco_py_dir}")
  endif()
endif()

find_path(MuJoCo_INCLUDE_DIR mujoco/mujoco.h HINTS ${_mujoco_hints} PATH_SUFFIXES include)

# La roue pip ne fournit que libmujoco.so.X.Y.Z (sans lien libmujoco.so) : on cherche par motif.
set(MuJoCo_LIBRARY "" CACHE FILEPATH "Bibliothèque MuJoCo")
if(NOT MuJoCo_LIBRARY)
  foreach(_dir ${_mujoco_hints})
    file(GLOB _cands "${_dir}/lib/libmujoco.so*" "${_dir}/libmujoco.so*"
                     "${_dir}/lib/libmujoco*.dylib" "${_dir}/libmujoco*.dylib")
    if(_cands)
      list(SORT _cands)
      list(GET _cands 0 _lib)
      set(MuJoCo_LIBRARY "${_lib}" CACHE FILEPATH "Bibliothèque MuJoCo" FORCE)
      break()
    endif()
  endforeach()
endif()
if(NOT MuJoCo_LIBRARY)
  find_library(MuJoCo_LIBRARY NAMES mujoco HINTS ${_mujoco_hints} PATH_SUFFIXES lib)
endif()

if(MuJoCo_INCLUDE_DIR AND EXISTS "${MuJoCo_INCLUDE_DIR}/mujoco/mujoco.h")
  file(STRINGS "${MuJoCo_INCLUDE_DIR}/mujoco/mujoco.h" _ver REGEX "^#define mjVERSION_HEADER")
  string(REGEX MATCH "[0-9]+" MuJoCo_VERSION "${_ver}")
endif()

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(MuJoCo
  REQUIRED_VARS MuJoCo_LIBRARY MuJoCo_INCLUDE_DIR
  VERSION_VAR MuJoCo_VERSION)

if(MuJoCo_FOUND AND NOT TARGET MuJoCo::MuJoCo)
  add_library(MuJoCo::MuJoCo SHARED IMPORTED)
  set_target_properties(MuJoCo::MuJoCo PROPERTIES
    IMPORTED_LOCATION "${MuJoCo_LIBRARY}"
    INTERFACE_INCLUDE_DIRECTORIES "${MuJoCo_INCLUDE_DIR}")
endif()
mark_as_advanced(MuJoCo_INCLUDE_DIR MuJoCo_LIBRARY)
