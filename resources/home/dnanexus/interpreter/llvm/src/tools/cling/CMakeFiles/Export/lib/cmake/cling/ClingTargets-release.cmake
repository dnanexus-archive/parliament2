#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "clingInterpreter" for configuration "Release"
set_property(TARGET clingInterpreter APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(clingInterpreter PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libclingInterpreter.a"
  )

list(APPEND _IMPORT_CHECK_TARGETS clingInterpreter )
list(APPEND _IMPORT_CHECK_FILES_FOR_clingInterpreter "${_IMPORT_PREFIX}/lib/libclingInterpreter.a" )

# Import target "clingMetaProcessor" for configuration "Release"
set_property(TARGET clingMetaProcessor APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(clingMetaProcessor PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libclingMetaProcessor.a"
  )

list(APPEND _IMPORT_CHECK_TARGETS clingMetaProcessor )
list(APPEND _IMPORT_CHECK_FILES_FOR_clingMetaProcessor "${_IMPORT_PREFIX}/lib/libclingMetaProcessor.a" )

# Import target "clingUtils" for configuration "Release"
set_property(TARGET clingUtils APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(clingUtils PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libclingUtils.a"
  )

list(APPEND _IMPORT_CHECK_TARGETS clingUtils )
list(APPEND _IMPORT_CHECK_FILES_FOR_clingUtils "${_IMPORT_PREFIX}/lib/libclingUtils.a" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
