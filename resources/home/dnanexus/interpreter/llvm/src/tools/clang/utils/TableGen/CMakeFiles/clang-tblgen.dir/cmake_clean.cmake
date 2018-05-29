file(REMOVE_RECURSE
  "../../../../bin/clang-tblgen.pdb"
  "../../../../bin/clang-tblgen"
)

# Per-language clean rules from dependency scanning.
foreach(lang CXX)
  include(CMakeFiles/clang-tblgen.dir/cmake_clean_${lang}.cmake OPTIONAL)
endforeach()
