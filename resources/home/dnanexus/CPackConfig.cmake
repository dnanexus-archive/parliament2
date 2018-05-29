# This file will be configured to contain variables for CPack. These variables
# should be set in the CMake list file of the project before CPack module is
# included. The list of available CPACK_xxx variables and their associated
# documentation may be obtained using
#  cpack --help-variable-list
#
# Some variables are common to all generators (e.g. CPACK_PACKAGE_NAME)
# and some are specific to a generator
# (e.g. CPACK_NSIS_EXTRA_INSTALL_COMMANDS). The generator specific variables
# usually begin with CPACK_<GENNAME>_xxxx.


set(CPACK_BINARY_7Z "")
set(CPACK_BINARY_BUNDLE "")
set(CPACK_BINARY_CYGWIN "")
set(CPACK_BINARY_DEB "OFF")
set(CPACK_BINARY_DRAGNDROP "")
set(CPACK_BINARY_FREEBSD "OFF")
set(CPACK_BINARY_IFW "OFF")
set(CPACK_BINARY_NSIS "OFF")
set(CPACK_BINARY_OSXX11 "")
set(CPACK_BINARY_PACKAGEMAKER "")
set(CPACK_BINARY_PRODUCTBUILD "")
set(CPACK_BINARY_RPM "OFF")
set(CPACK_BINARY_STGZ "ON")
set(CPACK_BINARY_TBZ2 "OFF")
set(CPACK_BINARY_TGZ "ON")
set(CPACK_BINARY_TXZ "OFF")
set(CPACK_BINARY_TZ "ON")
set(CPACK_BINARY_WIX "")
set(CPACK_BINARY_ZIP "")
set(CPACK_BUILD_SOURCE_DIRS "/home/dnanexus/root;/home/dnanexus")
set(CPACK_CMAKE_GENERATOR "Unix Makefiles")
set(CPACK_COMPONENTS_ALL "LLVMAnalysis;LLVMAsmParser;LLVMAsmPrinter;LLVMBinaryFormat;LLVMBitReader;LLVMBitWriter;LLVMCodeGen;LLVMCore;LLVMCoroutines;LLVMCoverage;LLVMDebugInfoCodeView;LLVMDebugInfoDWARF;LLVMDebugInfoMSF;LLVMDebugInfoPDB;LLVMDemangle;LLVMDlltoolDriver;LLVMExecutionEngine;LLVMGlobalISel;LLVMIRReader;LLVMInstCombine;LLVMInstrumentation;LLVMInterpreter;LLVMLTO;LLVMLibDriver;LLVMLineEditor;LLVMLinker;LLVMMC;LLVMMCDisassembler;LLVMMCJIT;LLVMMCParser;LLVMMIRParser;LLVMObjCARCOpts;LLVMObject;LLVMObjectYAML;LLVMOption;LLVMOrcJIT;LLVMPasses;LLVMProfileData;LLVMRuntimeDyld;LLVMScalarOpts;LLVMSelectionDAG;LLVMSupport;LLVMSymbolize;LLVMTableGen;LLVMTarget;LLVMTransformUtils;LLVMVectorize;LLVMX86AsmParser;LLVMX86AsmPrinter;LLVMX86CodeGen;LLVMX86Desc;LLVMX86Disassembler;LLVMX86Info;LLVMX86Utils;LLVMXRay;LLVMipo;LTO;Unspecified;applications;clang;clang-headers;clangAST;clangASTMatchers;clangAnalysis;clangBasic;clangCodeGen;clangDriver;clangDynamicASTMatchers;clangEdit;clangFormat;clangFrontend;clangFrontendTool;clangIndex;clangLex;clangParse;clangRewrite;clangRewriteFrontend;clangSema;clangSerialization;clangTooling;clangToolingCore;clangToolingRefactor;clingInterpreter;clingMetaProcessor;clingUtils;cmake-exports;headers;libraries;llvm-headers;opt-viewer;tests")
set(CPACK_COMPONENT_UNSPECIFIED_HIDDEN "TRUE")
set(CPACK_COMPONENT_UNSPECIFIED_REQUIRED "TRUE")
set(CPACK_GENERATOR "TGZ")
set(CPACK_INSTALL_CMAKE_PROJECTS "/home/dnanexus;ROOT;ALL;/")
set(CPACK_INSTALL_PREFIX "/usr/local")
set(CPACK_MODULE_PATH "/home/dnanexus/root/cmake/modules")
set(CPACK_NSIS_DISPLAY_NAME "root_v6.13.03")
set(CPACK_NSIS_INSTALLER_ICON_CODE "")
set(CPACK_NSIS_INSTALLER_MUI_ICON_CODE "")
set(CPACK_NSIS_INSTALL_ROOT "$PROGRAMFILES")
set(CPACK_NSIS_PACKAGE_NAME "root_v6.13.03")
set(CPACK_OUTPUT_CONFIG_FILE "/home/dnanexus/CPackConfig.cmake")
set(CPACK_PACKAGE_DEFAULT_LOCATION "/")
set(CPACK_PACKAGE_DESCRIPTION "ROOT project")
set(CPACK_PACKAGE_DESCRIPTION_FILE "/home/dnanexus/README.txt")
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "ROOT project")
set(CPACK_PACKAGE_EXECUTABLES "root;ROOT")
set(CPACK_PACKAGE_FILE_NAME "root_v6.13.03.Linux-ubuntu14-x86_64-gcc4.8.relwithdebinfo")
set(CPACK_PACKAGE_INSTALL_DIRECTORY "root_v6.13.03")
set(CPACK_PACKAGE_INSTALL_REGISTRY_KEY "root_v6.13.03")
set(CPACK_PACKAGE_NAME "ROOT")
set(CPACK_PACKAGE_RELOCATABLE "true")
set(CPACK_PACKAGE_VENDOR "HEPSoft")
set(CPACK_PACKAGE_VERSION "6.13.03")
set(CPACK_PACKAGE_VERSION_MAJOR "6")
set(CPACK_PACKAGE_VERSION_MINOR "13")
set(CPACK_PACKAGE_VERSION_PATCH "03")
set(CPACK_PROJECT_CONFIG_FILE "/home/dnanexus/CMakeCPackOptions.cmake")
set(CPACK_RESOURCE_FILE_LICENSE "/home/dnanexus/LICENSE.txt")
set(CPACK_RESOURCE_FILE_README "/home/dnanexus/README.txt")
set(CPACK_RESOURCE_FILE_WELCOME "/home/dnanexus/cmake-3.11.0-Linux-x86_64/share/cmake-3.11/Templates/CPack.GenericWelcome.txt")
set(CPACK_SET_DESTDIR "OFF")
set(CPACK_SOURCE_7Z "")
set(CPACK_SOURCE_CYGWIN "")
set(CPACK_SOURCE_GENERATOR "TGZ;TBZ2")
set(CPACK_SOURCE_IGNORE_FILES "/home/dnanexus;/home/dnanexus/root/tests;~$;/CVS/;/.svn/;/\\\\.svn/;/.git/;/\\\\.git/;\\\\.swp$;\\\\.swp$;\\.swp;\\\\.#;/#")
set(CPACK_SOURCE_OUTPUT_CONFIG_FILE "/home/dnanexus/CPackSourceConfig.cmake")
set(CPACK_SOURCE_RPM "OFF")
set(CPACK_SOURCE_STRIP_FILES "")
set(CPACK_SOURCE_TBZ2 "ON")
set(CPACK_SOURCE_TGZ "ON")
set(CPACK_SOURCE_TXZ "ON")
set(CPACK_SOURCE_TZ "ON")
set(CPACK_SOURCE_ZIP "OFF")
set(CPACK_SYSTEM_NAME "Linux")
set(CPACK_TOPLEVEL_TAG "Linux")
set(CPACK_WIX_SIZEOF_VOID_P "8")

if(NOT CPACK_PROPERTIES_FILE)
  set(CPACK_PROPERTIES_FILE "/home/dnanexus/CPackProperties.cmake")
endif()

if(EXISTS ${CPACK_PROPERTIES_FILE})
  include(${CPACK_PROPERTIES_FILE})
endif()

# Configuration for installation type "full"
list(APPEND CPACK_ALL_INSTALL_TYPES full)
set(CPACK_INSTALL_TYPE_FULL_DISPLAY_NAME "Full Installation")

# Configuration for installation type "minimal"
list(APPEND CPACK_ALL_INSTALL_TYPES minimal)
set(CPACK_INSTALL_TYPE_MINIMAL_DISPLAY_NAME "Minimal Installation")

# Configuration for installation type "developer"
list(APPEND CPACK_ALL_INSTALL_TYPES developer)
set(CPACK_INSTALL_TYPE_DEVELOPER_DISPLAY_NAME "Developer Installation")

# Configuration for component "applications"

SET(CPACK_COMPONENTS_ALL LLVMAnalysis LLVMAsmParser LLVMAsmPrinter LLVMBinaryFormat LLVMBitReader LLVMBitWriter LLVMCodeGen LLVMCore LLVMCoroutines LLVMCoverage LLVMDebugInfoCodeView LLVMDebugInfoDWARF LLVMDebugInfoMSF LLVMDebugInfoPDB LLVMDemangle LLVMDlltoolDriver LLVMExecutionEngine LLVMGlobalISel LLVMIRReader LLVMInstCombine LLVMInstrumentation LLVMInterpreter LLVMLTO LLVMLibDriver LLVMLineEditor LLVMLinker LLVMMC LLVMMCDisassembler LLVMMCJIT LLVMMCParser LLVMMIRParser LLVMObjCARCOpts LLVMObject LLVMObjectYAML LLVMOption LLVMOrcJIT LLVMPasses LLVMProfileData LLVMRuntimeDyld LLVMScalarOpts LLVMSelectionDAG LLVMSupport LLVMSymbolize LLVMTableGen LLVMTarget LLVMTransformUtils LLVMVectorize LLVMX86AsmParser LLVMX86AsmPrinter LLVMX86CodeGen LLVMX86Desc LLVMX86Disassembler LLVMX86Info LLVMX86Utils LLVMXRay LLVMipo LTO Unspecified applications clang clang-headers clangAST clangASTMatchers clangAnalysis clangBasic clangCodeGen clangDriver clangDynamicASTMatchers clangEdit clangFormat clangFrontend clangFrontendTool clangIndex clangLex clangParse clangRewrite clangRewriteFrontend clangSema clangSerialization clangTooling clangToolingCore clangToolingRefactor clingInterpreter clingMetaProcessor clingUtils cmake-exports headers libraries llvm-headers opt-viewer tests)
set(CPACK_COMPONENT_APPLICATIONS_DISPLAY_NAME "ROOT Applications")
set(CPACK_COMPONENT_APPLICATIONS_DESCRIPTION "ROOT executables such as root.exe")
set(CPACK_COMPONENT_APPLICATIONS_INSTALL_TYPES full minimal developer)

# Configuration for component "libraries"

SET(CPACK_COMPONENTS_ALL LLVMAnalysis LLVMAsmParser LLVMAsmPrinter LLVMBinaryFormat LLVMBitReader LLVMBitWriter LLVMCodeGen LLVMCore LLVMCoroutines LLVMCoverage LLVMDebugInfoCodeView LLVMDebugInfoDWARF LLVMDebugInfoMSF LLVMDebugInfoPDB LLVMDemangle LLVMDlltoolDriver LLVMExecutionEngine LLVMGlobalISel LLVMIRReader LLVMInstCombine LLVMInstrumentation LLVMInterpreter LLVMLTO LLVMLibDriver LLVMLineEditor LLVMLinker LLVMMC LLVMMCDisassembler LLVMMCJIT LLVMMCParser LLVMMIRParser LLVMObjCARCOpts LLVMObject LLVMObjectYAML LLVMOption LLVMOrcJIT LLVMPasses LLVMProfileData LLVMRuntimeDyld LLVMScalarOpts LLVMSelectionDAG LLVMSupport LLVMSymbolize LLVMTableGen LLVMTarget LLVMTransformUtils LLVMVectorize LLVMX86AsmParser LLVMX86AsmPrinter LLVMX86CodeGen LLVMX86Desc LLVMX86Disassembler LLVMX86Info LLVMX86Utils LLVMXRay LLVMipo LTO Unspecified applications clang clang-headers clangAST clangASTMatchers clangAnalysis clangBasic clangCodeGen clangDriver clangDynamicASTMatchers clangEdit clangFormat clangFrontend clangFrontendTool clangIndex clangLex clangParse clangRewrite clangRewriteFrontend clangSema clangSerialization clangTooling clangToolingCore clangToolingRefactor clingInterpreter clingMetaProcessor clingUtils cmake-exports headers libraries llvm-headers opt-viewer tests)
set(CPACK_COMPONENT_LIBRARIES_DISPLAY_NAME "ROOT Libraries")
set(CPACK_COMPONENT_LIBRARIES_DESCRIPTION "All ROOT libraries and dictionaries")
set(CPACK_COMPONENT_LIBRARIES_INSTALL_TYPES full minimal developer)

# Configuration for component "headers"

SET(CPACK_COMPONENTS_ALL LLVMAnalysis LLVMAsmParser LLVMAsmPrinter LLVMBinaryFormat LLVMBitReader LLVMBitWriter LLVMCodeGen LLVMCore LLVMCoroutines LLVMCoverage LLVMDebugInfoCodeView LLVMDebugInfoDWARF LLVMDebugInfoMSF LLVMDebugInfoPDB LLVMDemangle LLVMDlltoolDriver LLVMExecutionEngine LLVMGlobalISel LLVMIRReader LLVMInstCombine LLVMInstrumentation LLVMInterpreter LLVMLTO LLVMLibDriver LLVMLineEditor LLVMLinker LLVMMC LLVMMCDisassembler LLVMMCJIT LLVMMCParser LLVMMIRParser LLVMObjCARCOpts LLVMObject LLVMObjectYAML LLVMOption LLVMOrcJIT LLVMPasses LLVMProfileData LLVMRuntimeDyld LLVMScalarOpts LLVMSelectionDAG LLVMSupport LLVMSymbolize LLVMTableGen LLVMTarget LLVMTransformUtils LLVMVectorize LLVMX86AsmParser LLVMX86AsmPrinter LLVMX86CodeGen LLVMX86Desc LLVMX86Disassembler LLVMX86Info LLVMX86Utils LLVMXRay LLVMipo LTO Unspecified applications clang clang-headers clangAST clangASTMatchers clangAnalysis clangBasic clangCodeGen clangDriver clangDynamicASTMatchers clangEdit clangFormat clangFrontend clangFrontendTool clangIndex clangLex clangParse clangRewrite clangRewriteFrontend clangSema clangSerialization clangTooling clangToolingCore clangToolingRefactor clingInterpreter clingMetaProcessor clingUtils cmake-exports headers libraries llvm-headers opt-viewer tests)
set(CPACK_COMPONENT_HEADERS_DISPLAY_NAME "C++ Headers")
set(CPACK_COMPONENT_HEADERS_DESCRIPTION "These are needed to do any development")
set(CPACK_COMPONENT_HEADERS_INSTALL_TYPES full developer)

# Configuration for component "tests"

SET(CPACK_COMPONENTS_ALL LLVMAnalysis LLVMAsmParser LLVMAsmPrinter LLVMBinaryFormat LLVMBitReader LLVMBitWriter LLVMCodeGen LLVMCore LLVMCoroutines LLVMCoverage LLVMDebugInfoCodeView LLVMDebugInfoDWARF LLVMDebugInfoMSF LLVMDebugInfoPDB LLVMDemangle LLVMDlltoolDriver LLVMExecutionEngine LLVMGlobalISel LLVMIRReader LLVMInstCombine LLVMInstrumentation LLVMInterpreter LLVMLTO LLVMLibDriver LLVMLineEditor LLVMLinker LLVMMC LLVMMCDisassembler LLVMMCJIT LLVMMCParser LLVMMIRParser LLVMObjCARCOpts LLVMObject LLVMObjectYAML LLVMOption LLVMOrcJIT LLVMPasses LLVMProfileData LLVMRuntimeDyld LLVMScalarOpts LLVMSelectionDAG LLVMSupport LLVMSymbolize LLVMTableGen LLVMTarget LLVMTransformUtils LLVMVectorize LLVMX86AsmParser LLVMX86AsmPrinter LLVMX86CodeGen LLVMX86Desc LLVMX86Disassembler LLVMX86Info LLVMX86Utils LLVMXRay LLVMipo LTO Unspecified applications clang clang-headers clangAST clangASTMatchers clangAnalysis clangBasic clangCodeGen clangDriver clangDynamicASTMatchers clangEdit clangFormat clangFrontend clangFrontendTool clangIndex clangLex clangParse clangRewrite clangRewriteFrontend clangSema clangSerialization clangTooling clangToolingCore clangToolingRefactor clingInterpreter clingMetaProcessor clingUtils cmake-exports headers libraries llvm-headers opt-viewer tests)
set(CPACK_COMPONENT_TESTS_DISPLAY_NAME "ROOT Tests and Tutorials")
set(CPACK_COMPONENT_TESTS_DESCRIPTION "These are needed to do any test and tutorial")
set(CPACK_COMPONENT_TESTS_INSTALL_TYPES full developer)
