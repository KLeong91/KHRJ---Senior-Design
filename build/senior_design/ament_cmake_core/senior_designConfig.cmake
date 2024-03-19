# generated from ament/cmake/core/templates/nameConfig.cmake.in

# prevent multiple inclusion
if(_senior_design_CONFIG_INCLUDED)
  # ensure to keep the found flag the same
  if(NOT DEFINED senior_design_FOUND)
    # explicitly set it to FALSE, otherwise CMake will set it to TRUE
    set(senior_design_FOUND FALSE)
  elseif(NOT senior_design_FOUND)
    # use separate condition to avoid uninitialized variable warning
    set(senior_design_FOUND FALSE)
  endif()
  return()
endif()
set(_senior_design_CONFIG_INCLUDED TRUE)

# output package information
if(NOT senior_design_FIND_QUIETLY)
  message(STATUS "Found senior_design: 0.0.0 (${senior_design_DIR})")
endif()

# warn when using a deprecated package
if(NOT "" STREQUAL "")
  set(_msg "Package 'senior_design' is deprecated")
  # append custom deprecation text if available
  if(NOT "" STREQUAL "TRUE")
    set(_msg "${_msg} ()")
  endif()
  # optionally quiet the deprecation message
  if(NOT ${senior_design_DEPRECATED_QUIET})
    message(DEPRECATION "${_msg}")
  endif()
endif()

# flag package as ament-based to distinguish it after being find_package()-ed
set(senior_design_FOUND_AMENT_PACKAGE TRUE)

# include all config extra files
set(_extras "")
foreach(_extra ${_extras})
  include("${senior_design_DIR}/${_extra}")
endforeach()
