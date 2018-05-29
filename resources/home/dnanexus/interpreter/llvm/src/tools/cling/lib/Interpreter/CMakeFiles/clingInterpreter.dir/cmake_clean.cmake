file(REMOVE_RECURSE
  "../../../../lib/libclingInterpreter.pdb"
  "../../../../lib/libclingInterpreter.a"
)

# Per-language clean rules from dependency scanning.
foreach(lang CXX)
  include(CMakeFiles/clingInterpreter.dir/cmake_clean_${lang}.cmake OPTIONAL)
endforeach()
