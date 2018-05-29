# Distributed under the OSI-approved BSD 3-Clause License.  See accompanying
# file Copyright.txt or https://cmake.org/licensing for details.

cmake_minimum_required(VERSION 3.5)

if("/home/dnanexus/root/graf2d/freetype/src/freetype-2.6.1.tar.gz" STREQUAL "")
  message(FATAL_ERROR "LOCAL can't be empty")
endif()

if(NOT EXISTS "/home/dnanexus/root/graf2d/freetype/src/freetype-2.6.1.tar.gz")
  message(FATAL_ERROR "File not found: /home/dnanexus/root/graf2d/freetype/src/freetype-2.6.1.tar.gz")
endif()

if("SHA256" STREQUAL "")
  message(WARNING "File will not be verified since no URL_HASH specified")
  return()
endif()

if("0a3c7dfbda6da1e8fce29232e8e96d987ababbbf71ebc8c75659e4132c367014" STREQUAL "")
  message(FATAL_ERROR "EXPECT_VALUE can't be empty")
endif()

message(STATUS "verifying file...
     file='/home/dnanexus/root/graf2d/freetype/src/freetype-2.6.1.tar.gz'")

file("SHA256" "/home/dnanexus/root/graf2d/freetype/src/freetype-2.6.1.tar.gz" actual_value)

if(NOT "${actual_value}" STREQUAL "0a3c7dfbda6da1e8fce29232e8e96d987ababbbf71ebc8c75659e4132c367014")
  message(FATAL_ERROR "error: SHA256 hash of
  /home/dnanexus/root/graf2d/freetype/src/freetype-2.6.1.tar.gz
does not match expected value
  expected: '0a3c7dfbda6da1e8fce29232e8e96d987ababbbf71ebc8c75659e4132c367014'
    actual: '${actual_value}'
")
endif()

message(STATUS "verifying file... done")
