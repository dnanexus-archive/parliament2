

set(command "${make}")
execute_process(
  COMMAND ${command}
  RESULT_VARIABLE result
  OUTPUT_FILE "/home/dnanexus/FREETYPE-prefix/src/FREETYPE-stamp/FREETYPE-build-out.log"
  ERROR_FILE "/home/dnanexus/FREETYPE-prefix/src/FREETYPE-stamp/FREETYPE-build-err.log"
  )
if(result)
  set(msg "Command failed: ${result}\n")
  foreach(arg IN LISTS command)
    set(msg "${msg} '${arg}'")
  endforeach()
  set(msg "${msg}\nSee also\n  /home/dnanexus/FREETYPE-prefix/src/FREETYPE-stamp/FREETYPE-build-*.log")
  message(FATAL_ERROR "${msg}")
else()
  set(msg "FREETYPE build command succeeded.  See also /home/dnanexus/FREETYPE-prefix/src/FREETYPE-stamp/FREETYPE-build-*.log")
  message(STATUS "${msg}")
endif()
