

set(command "${make};install")
execute_process(
  COMMAND ${command}
  RESULT_VARIABLE result
  OUTPUT_FILE "/home/dnanexus/LZMA-prefix/src/LZMA-stamp/LZMA-install-out.log"
  ERROR_FILE "/home/dnanexus/LZMA-prefix/src/LZMA-stamp/LZMA-install-err.log"
  )
if(result)
  set(msg "Command failed: ${result}\n")
  foreach(arg IN LISTS command)
    set(msg "${msg} '${arg}'")
  endforeach()
  set(msg "${msg}\nSee also\n  /home/dnanexus/LZMA-prefix/src/LZMA-stamp/LZMA-install-*.log")
  message(FATAL_ERROR "${msg}")
else()
  set(msg "LZMA install command succeeded.  See also /home/dnanexus/LZMA-prefix/src/LZMA-stamp/LZMA-install-*.log")
  message(STATUS "${msg}")
endif()
