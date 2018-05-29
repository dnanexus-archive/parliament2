

set(command "${make}")
execute_process(
  COMMAND ${command}
  RESULT_VARIABLE result
  OUTPUT_FILE "/home/dnanexus/LZMA-prefix/src/LZMA-stamp/LZMA-build-out.log"
  ERROR_FILE "/home/dnanexus/LZMA-prefix/src/LZMA-stamp/LZMA-build-err.log"
  )
if(result)
  set(msg "Command failed: ${result}\n")
  foreach(arg IN LISTS command)
    set(msg "${msg} '${arg}'")
  endforeach()
  set(msg "${msg}\nSee also\n  /home/dnanexus/LZMA-prefix/src/LZMA-stamp/LZMA-build-*.log")
  message(FATAL_ERROR "${msg}")
else()
  set(msg "LZMA build command succeeded.  See also /home/dnanexus/LZMA-prefix/src/LZMA-stamp/LZMA-build-*.log")
  message(STATUS "${msg}")
endif()
