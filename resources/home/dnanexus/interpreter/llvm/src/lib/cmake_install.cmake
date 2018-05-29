# Install script for directory: /home/dnanexus/root/interpreter/llvm/src/lib

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
    set(CMAKE_INSTALL_CONFIG_NAME "Release")
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

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for each subdirectory.
  include("/home/dnanexus/interpreter/llvm/src/lib/IR/cmake_install.cmake")
  include("/home/dnanexus/interpreter/llvm/src/lib/IRReader/cmake_install.cmake")
  include("/home/dnanexus/interpreter/llvm/src/lib/CodeGen/cmake_install.cmake")
  include("/home/dnanexus/interpreter/llvm/src/lib/BinaryFormat/cmake_install.cmake")
  include("/home/dnanexus/interpreter/llvm/src/lib/Bitcode/cmake_install.cmake")
  include("/home/dnanexus/interpreter/llvm/src/lib/Transforms/cmake_install.cmake")
  include("/home/dnanexus/interpreter/llvm/src/lib/Linker/cmake_install.cmake")
  include("/home/dnanexus/interpreter/llvm/src/lib/Analysis/cmake_install.cmake")
  include("/home/dnanexus/interpreter/llvm/src/lib/LTO/cmake_install.cmake")
  include("/home/dnanexus/interpreter/llvm/src/lib/MC/cmake_install.cmake")
  include("/home/dnanexus/interpreter/llvm/src/lib/Object/cmake_install.cmake")
  include("/home/dnanexus/interpreter/llvm/src/lib/ObjectYAML/cmake_install.cmake")
  include("/home/dnanexus/interpreter/llvm/src/lib/Option/cmake_install.cmake")
  include("/home/dnanexus/interpreter/llvm/src/lib/DebugInfo/cmake_install.cmake")
  include("/home/dnanexus/interpreter/llvm/src/lib/ExecutionEngine/cmake_install.cmake")
  include("/home/dnanexus/interpreter/llvm/src/lib/Target/cmake_install.cmake")
  include("/home/dnanexus/interpreter/llvm/src/lib/AsmParser/cmake_install.cmake")
  include("/home/dnanexus/interpreter/llvm/src/lib/LineEditor/cmake_install.cmake")
  include("/home/dnanexus/interpreter/llvm/src/lib/ProfileData/cmake_install.cmake")
  include("/home/dnanexus/interpreter/llvm/src/lib/Fuzzer/cmake_install.cmake")
  include("/home/dnanexus/interpreter/llvm/src/lib/Passes/cmake_install.cmake")
  include("/home/dnanexus/interpreter/llvm/src/lib/ToolDrivers/cmake_install.cmake")
  include("/home/dnanexus/interpreter/llvm/src/lib/XRay/cmake_install.cmake")
  include("/home/dnanexus/interpreter/llvm/src/lib/Testing/cmake_install.cmake")

endif()

