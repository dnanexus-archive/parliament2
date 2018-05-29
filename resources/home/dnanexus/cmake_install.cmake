# Install script for directory: /home/dnanexus/root

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/usr/local")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "RelWithDebInfo")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "1")
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xlibrariesx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE DIRECTORY FILES "/home/dnanexus/lib/" FILES_MATCHING REGEX "/libtbb[^/]*$")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xheadersx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include" TYPE FILE FILES "/home/dnanexus/include/module.modulemap")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/etc" TYPE FILE FILES "/home/dnanexus/etc/allDict.cxx.pch")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/etc" TYPE DIRECTORY FILES "/home/dnanexus/etc/dictpch")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xtestsx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/tutorials" TYPE FILE FILES "/home/dnanexus/tutorials/hsimple.root")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include" TYPE FILE FILES "/home/dnanexus/include/RConfigure.h")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/cmake" TYPE FILE FILES
    "/home/dnanexus/ROOTConfig-version.cmake"
    "/home/dnanexus/installtree/ROOTUseFile.cmake"
    "/home/dnanexus/installtree/ROOTConfig.cmake"
    )
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/cmake/ROOTConfig-targets.cmake")
    file(DIFFERENT EXPORT_FILE_CHANGED FILES
         "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/cmake/ROOTConfig-targets.cmake"
         "/home/dnanexus/CMakeFiles/Export/cmake/ROOTConfig-targets.cmake")
    if(EXPORT_FILE_CHANGED)
      file(GLOB OLD_CONFIG_FILES "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/cmake/ROOTConfig-targets-*.cmake")
      if(OLD_CONFIG_FILES)
        message(STATUS "Old export file \"$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/cmake/ROOTConfig-targets.cmake\" will be replaced.  Removing files [${OLD_CONFIG_FILES}].")
        file(REMOVE ${OLD_CONFIG_FILES})
      endif()
    endif()
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/cmake" TYPE FILE FILES "/home/dnanexus/CMakeFiles/Export/cmake/ROOTConfig-targets.cmake")
  if("${CMAKE_INSTALL_CONFIG_NAME}" MATCHES "^([Rr][Ee][Ll][Ww][Ii][Tt][Hh][Dd][Ee][Bb][Ii][Nn][Ff][Oo])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/cmake" TYPE FILE FILES "/home/dnanexus/CMakeFiles/Export/cmake/ROOTConfig-targets-relwithdebinfo.cmake")
  endif()
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/bin" TYPE FILE PERMISSIONS OWNER_WRITE OWNER_READ GROUP_READ WORLD_READ FILES
    "/home/dnanexus/bin/thisroot.sh"
    "/home/dnanexus/bin/thisroot.csh"
    "/home/dnanexus/bin/setxrd.csh"
    "/home/dnanexus/bin/setxrd.sh"
    )
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/bin" TYPE FILE PERMISSIONS OWNER_EXECUTE OWNER_WRITE OWNER_READ GROUP_EXECUTE GROUP_READ WORLD_EXECUTE WORLD_READ FILES
    "/home/dnanexus/bin/memprobe"
    "/home/dnanexus/installtree/root-config"
    "/home/dnanexus/root/cmake/scripts/setenvwrap.csh"
    "/home/dnanexus/bin/roots"
    "/home/dnanexus/bin/proofserv"
    )
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include" TYPE FILE FILES
    "/home/dnanexus/include/RConfigOptions.h"
    "/home/dnanexus/include/compiledata.h"
    )
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/etc" TYPE FILE FILES
    "/home/dnanexus/etc/root.mimes"
    "/home/dnanexus/etc/system.rootrc"
    "/home/dnanexus/etc/system.rootauthrc"
    "/home/dnanexus/etc/system.rootdaemonrc"
    )
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/etc/daemons" TYPE FILE PERMISSIONS OWNER_EXECUTE OWNER_WRITE OWNER_READ GROUP_EXECUTE GROUP_READ WORLD_EXECUTE WORLD_READ FILES
    "/home/dnanexus/etc/daemons/rootd.rc.d"
    "/home/dnanexus/etc/daemons/proofd.rc.d"
    )
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/etc/daemons" TYPE FILE FILES
    "/home/dnanexus/etc/daemons/rootd.xinetd"
    "/home/dnanexus/etc/daemons/proofd.xinetd"
    )
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/emacs/site-lisp" TYPE FILE FILES "/home/dnanexus/root-help.el")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/config" TYPE FILE FILES
    "/home/dnanexus/config/Makefile.comp"
    "/home/dnanexus/config/Makefile.config"
    )
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/." TYPE FILE FILES "/home/dnanexus/root/LICENSE")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/." TYPE DIRECTORY FILES "/home/dnanexus/root/README")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/etc" TYPE DIRECTORY FILES "/home/dnanexus/root/etc/" USE_SOURCE_PERMISSIONS REGEX "/system\\.rootrc$" EXCLUDE REGEX "/system\\.rootauthrc$" EXCLUDE REGEX "/system\\.rootdaemonrc$" EXCLUDE REGEX "/rootd\\.rc\\.d$" EXCLUDE REGEX "/proofd\\.rc\\.d$" EXCLUDE REGEX "/rootd\\.xinetd$" EXCLUDE REGEX "/proofd\\.xinetd$" EXCLUDE REGEX "/root\\.mimes$" EXCLUDE REGEX "/cmake$" EXCLUDE REGEX "/http$" EXCLUDE)
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/fonts" TYPE DIRECTORY FILES "/home/dnanexus/root/fonts/")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/icons" TYPE DIRECTORY FILES "/home/dnanexus/root/icons/")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/macros" TYPE DIRECTORY FILES "/home/dnanexus/root/macros/")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/man" TYPE DIRECTORY FILES "/home/dnanexus/root/man/")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xtestsx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/test" TYPE DIRECTORY FILES "/home/dnanexus/root/test/")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xtestsx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/tutorials" TYPE DIRECTORY FILES "/home/dnanexus/root/tutorials/")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/cmake" TYPE DIRECTORY FILES "/home/dnanexus/root/cmake/modules" REGEX "/Find[^/]*\\.cmake$" EXCLUDE)
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/aclocal" TYPE FILE FILES "/home/dnanexus/root/build/misc/root.m4")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for each subdirectory.
  include("/home/dnanexus/builtins/xxhash/cmake_install.cmake")
  include("/home/dnanexus/builtins/lz4/cmake_install.cmake")
  include("/home/dnanexus/interpreter/cmake_install.cmake")
  include("/home/dnanexus/core/cmake_install.cmake")
  include("/home/dnanexus/build/cmake_install.cmake")
  include("/home/dnanexus/math/cmake_install.cmake")
  include("/home/dnanexus/hist/cmake_install.cmake")
  include("/home/dnanexus/tree/cmake_install.cmake")
  include("/home/dnanexus/io/cmake_install.cmake")
  include("/home/dnanexus/net/cmake_install.cmake")
  include("/home/dnanexus/graf2d/cmake_install.cmake")
  include("/home/dnanexus/graf3d/cmake_install.cmake")
  include("/home/dnanexus/gui/cmake_install.cmake")
  include("/home/dnanexus/proof/cmake_install.cmake")
  include("/home/dnanexus/html/cmake_install.cmake")
  include("/home/dnanexus/montecarlo/cmake_install.cmake")
  include("/home/dnanexus/geom/cmake_install.cmake")
  include("/home/dnanexus/rootx/cmake_install.cmake")
  include("/home/dnanexus/misc/cmake_install.cmake")
  include("/home/dnanexus/main/cmake_install.cmake")
  include("/home/dnanexus/bindings/cmake_install.cmake")
  include("/home/dnanexus/sql/cmake_install.cmake")
  include("/home/dnanexus/tmva/cmake_install.cmake")
  include("/home/dnanexus/roofit/cmake_install.cmake")

endif()

if(CMAKE_INSTALL_COMPONENT)
  set(CMAKE_INSTALL_MANIFEST "install_manifest_${CMAKE_INSTALL_COMPONENT}.txt")
else()
  set(CMAKE_INSTALL_MANIFEST "install_manifest.txt")
endif()

string(REPLACE ";" "\n" CMAKE_INSTALL_MANIFEST_CONTENT
       "${CMAKE_INSTALL_MANIFEST_FILES}")
file(WRITE "/home/dnanexus/${CMAKE_INSTALL_MANIFEST}"
     "${CMAKE_INSTALL_MANIFEST_CONTENT}")
