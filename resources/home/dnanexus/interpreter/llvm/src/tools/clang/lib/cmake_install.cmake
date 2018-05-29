# Install script for directory: /home/dnanexus/root/interpreter/llvm/src/tools/clang/lib

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
  include("/home/dnanexus/interpreter/llvm/src/tools/clang/lib/Headers/cmake_install.cmake")
  include("/home/dnanexus/interpreter/llvm/src/tools/clang/lib/Basic/cmake_install.cmake")
  include("/home/dnanexus/interpreter/llvm/src/tools/clang/lib/Lex/cmake_install.cmake")
  include("/home/dnanexus/interpreter/llvm/src/tools/clang/lib/Parse/cmake_install.cmake")
  include("/home/dnanexus/interpreter/llvm/src/tools/clang/lib/AST/cmake_install.cmake")
  include("/home/dnanexus/interpreter/llvm/src/tools/clang/lib/ASTMatchers/cmake_install.cmake")
  include("/home/dnanexus/interpreter/llvm/src/tools/clang/lib/Sema/cmake_install.cmake")
  include("/home/dnanexus/interpreter/llvm/src/tools/clang/lib/CodeGen/cmake_install.cmake")
  include("/home/dnanexus/interpreter/llvm/src/tools/clang/lib/Analysis/cmake_install.cmake")
  include("/home/dnanexus/interpreter/llvm/src/tools/clang/lib/Edit/cmake_install.cmake")
  include("/home/dnanexus/interpreter/llvm/src/tools/clang/lib/Rewrite/cmake_install.cmake")
  include("/home/dnanexus/interpreter/llvm/src/tools/clang/lib/Driver/cmake_install.cmake")
  include("/home/dnanexus/interpreter/llvm/src/tools/clang/lib/Serialization/cmake_install.cmake")
  include("/home/dnanexus/interpreter/llvm/src/tools/clang/lib/Frontend/cmake_install.cmake")
  include("/home/dnanexus/interpreter/llvm/src/tools/clang/lib/FrontendTool/cmake_install.cmake")
  include("/home/dnanexus/interpreter/llvm/src/tools/clang/lib/Tooling/cmake_install.cmake")
  include("/home/dnanexus/interpreter/llvm/src/tools/clang/lib/Index/cmake_install.cmake")
  include("/home/dnanexus/interpreter/llvm/src/tools/clang/lib/Format/cmake_install.cmake")

endif()

