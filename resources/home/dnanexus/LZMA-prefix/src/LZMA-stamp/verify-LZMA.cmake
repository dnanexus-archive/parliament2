# Distributed under the OSI-approved BSD 3-Clause License.  See accompanying
# file Copyright.txt or https://cmake.org/licensing for details.

cmake_minimum_required(VERSION 3.5)

if("/home/dnanexus/root/core/lzma/src/xz-5.2.1.tar.gz" STREQUAL "")
  message(FATAL_ERROR "LOCAL can't be empty")
endif()

if(NOT EXISTS "/home/dnanexus/root/core/lzma/src/xz-5.2.1.tar.gz")
  message(FATAL_ERROR "File not found: /home/dnanexus/root/core/lzma/src/xz-5.2.1.tar.gz")
endif()

if("SHA256" STREQUAL "")
  message(WARNING "File will not be verified since no URL_HASH specified")
  return()
endif()

if("b918b6648076e74f8d7ae19db5ee663df800049e187259faf5eb997a7b974681" STREQUAL "")
  message(FATAL_ERROR "EXPECT_VALUE can't be empty")
endif()

message(STATUS "verifying file...
     file='/home/dnanexus/root/core/lzma/src/xz-5.2.1.tar.gz'")

file("SHA256" "/home/dnanexus/root/core/lzma/src/xz-5.2.1.tar.gz" actual_value)

if(NOT "${actual_value}" STREQUAL "b918b6648076e74f8d7ae19db5ee663df800049e187259faf5eb997a7b974681")
  message(FATAL_ERROR "error: SHA256 hash of
  /home/dnanexus/root/core/lzma/src/xz-5.2.1.tar.gz
does not match expected value
  expected: 'b918b6648076e74f8d7ae19db5ee663df800049e187259faf5eb997a7b974681'
    actual: '${actual_value}'
")
endif()

message(STATUS "verifying file... done")
