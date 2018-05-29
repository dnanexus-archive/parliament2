file(REMOVE_RECURSE
  "../libLLVMFuzzerNoMain.pdb"
  "../libLLVMFuzzerNoMain.a"
)

# Per-language clean rules from dependency scanning.
foreach(lang CXX)
  include(CMakeFiles/LLVMFuzzerNoMain.dir/cmake_clean_${lang}.cmake OPTIONAL)
endforeach()
