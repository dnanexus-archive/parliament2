#.rst:
# FindUMESIMD
# -----------
#
# Find the UME::SIMD library headers and define variables.
#
# Result Variables
# ^^^^^^^^^^^^^^^^
#
# This module defines the following variables:
#
# ::
#
#   UMESIMD_FOUND          - True if UME::SIMD is found.
#   UMESIMD_INCLUDE_DIRS   - Where to find umesimd/UMESimd.h
#
# ::
#
#   UMESIMD_VERSION        - The version of UME::SIMD found (x.y.z)
#   UMESIMD_VERSION_MAJOR  - The major version of UME::SIMD
#   UMESIMD_VERSION_MINOR  - The minor version of UME::SIMD
#   UMESIMD_VERSION_PATCH  - The patch version of UME::SIMD
#
# Hints
# ^^^^^
#
# A user may set the ``UMESIMD_ROOT`` environment variable to a UME::SIMD
# installation root to tell this module where to look.

set(_UMESIMD_PATHS)

if(UMESIMD_ROOT)
  list(APPEND _UMESIMD_PATHS "${UMESIMD_ROOT}")
endif()

if(EXISTS $ENV{UMESIMD_ROOT})
  list(APPEND _UMESIMD_PATHS "$ENV{UMESIMD_ROOT}")
endif()

find_path(UMESIMD_INCLUDE_DIR NAMES umesimd/UMESimd.h PATHS ${_UMESIMD_PATHS} PATH_SUFFIXES include)

mark_as_advanced(UMESIMD_INCLUDE_DIR)

if(UMESIMD_INCLUDE_DIR)
  set(UMESIMD_VERSION_FILE "${UMESIMD_INCLUDE_DIR}/umesimd/UMESimd.h")
  if (EXISTS "${UMESIMD_VERSION_FILE}")
    file(STRINGS "${UMESIMD_VERSION_FILE}" UMESIMD_VERSION_PARTS REGEX "#define UME_SIMD_VERSION_[A-Z]+[ ]+")
    string(REGEX REPLACE ".+UME_SIMD_VERSION_MAJOR[ ]+([0-9]+).*" "\\1" UMESIMD_VERSION_MAJOR "${UMESIMD_VERSION_PARTS}")
    string(REGEX REPLACE ".+UME_SIMD_VERSION_MINOR[ ]+([0-9]+).*" "\\1" UMESIMD_VERSION_MINOR "${UMESIMD_VERSION_PARTS}")
    string(REGEX REPLACE ".+UME_SIMD_VERSION_PATCH[ ]+([0-9]+).*" "\\1" UMESIMD_VERSION_PATCH "${UMESIMD_VERSION_PARTS}")
    set(UMESIMD_VERSION "${UMESIMD_VERSION_MAJOR}.${UMESIMD_VERSION_MINOR}.${UMESIMD_VERSION_PATCH}")
    set(UMESIMD_INCLUDE_DIRS ${UMESIMD_INCLUDE_DIR})
  endif()
endif()

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(UMESIMD
  REQUIRED_VARS UMESIMD_INCLUDE_DIRS VERSION_VAR UMESIMD_VERSION)
