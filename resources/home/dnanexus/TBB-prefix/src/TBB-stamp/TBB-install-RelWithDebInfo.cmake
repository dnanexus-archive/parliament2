

set(command "/home/dnanexus/cmake-3.11.0-Linux-x86_64/bin/cmake;-Dinstall_dir=/home/dnanexus;-Dsource_dir=/home/dnanexus/TBB-prefix/src/TBB;-P;/home/dnanexus/root/cmake/scripts/InstallTBB.cmake")
execute_process(
  COMMAND ${command}
  RESULT_VARIABLE result
  OUTPUT_FILE "/home/dnanexus/TBB-prefix/src/TBB-stamp/TBB-install-out.log"
  ERROR_FILE "/home/dnanexus/TBB-prefix/src/TBB-stamp/TBB-install-err.log"
  )
if(result)
  set(msg "Command failed: ${result}\n")
  foreach(arg IN LISTS command)
    set(msg "${msg} '${arg}'")
  endforeach()
  set(msg "${msg}\nSee also\n  /home/dnanexus/TBB-prefix/src/TBB-stamp/TBB-install-*.log")
  message(FATAL_ERROR "${msg}")
else()
  set(msg "TBB install command succeeded.  See also /home/dnanexus/TBB-prefix/src/TBB-stamp/TBB-install-*.log")
  message(STATUS "${msg}")
endif()
