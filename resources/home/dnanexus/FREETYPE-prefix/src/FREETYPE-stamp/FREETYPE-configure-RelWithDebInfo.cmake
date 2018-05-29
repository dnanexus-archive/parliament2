

set(command "./configure;--prefix;/home/dnanexus/FREETYPE-prefix;--with-pic;--disable-shared;--with-png=no;--with-bzip2=no;--with-harfbuzz=no;CC=/usr/bin/cc;CFLAGS=-O")
execute_process(
  COMMAND ${command}
  RESULT_VARIABLE result
  OUTPUT_FILE "/home/dnanexus/FREETYPE-prefix/src/FREETYPE-stamp/FREETYPE-configure-out.log"
  ERROR_FILE "/home/dnanexus/FREETYPE-prefix/src/FREETYPE-stamp/FREETYPE-configure-err.log"
  )
if(result)
  set(msg "Command failed: ${result}\n")
  foreach(arg IN LISTS command)
    set(msg "${msg} '${arg}'")
  endforeach()
  set(msg "${msg}\nSee also\n  /home/dnanexus/FREETYPE-prefix/src/FREETYPE-stamp/FREETYPE-configure-*.log")
  message(FATAL_ERROR "${msg}")
else()
  set(msg "FREETYPE configure command succeeded.  See also /home/dnanexus/FREETYPE-prefix/src/FREETYPE-stamp/FREETYPE-configure-*.log")
  message(STATUS "${msg}")
endif()
