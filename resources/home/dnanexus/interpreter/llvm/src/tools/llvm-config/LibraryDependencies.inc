//===- llvm-build generated file --------------------------------*- C++ -*-===//
//
// Component Library Depenedency Table
//
// Automatically generated file, do not edit!
//
//===----------------------------------------------------------------------===//

struct AvailableComponent {
  /// The name of the component.
  const char *Name;

  /// The name of the library for this component (or NULL).
  const char *Library;

  /// Whether the component is installed.
  bool IsInstalled;

  /// The list of libraries required when linking this component.
  const char *RequiredLibraries[18];
} AvailableComponents[64] = {
  { "all", nullptr, true, { "coroutines", "interpreter", "engine", "gtest_main", "libdriver", "objectyaml", "all-targets", "testingsupport", "mirparser", "coverage", "orcjit", "lineeditor", "dlltooldriver", "nativecodegen", "tablegen", "symbolize", "lto" } },
  { "all-targets", nullptr, true, { "x86" } },
  { "analysis", "LLVMAnalysis", true, { "binaryformat", "core", "object", "profiledata", "support" } },
  { "asmparser", "LLVMAsmParser", true, { "binaryformat", "core", "support" } },
  { "asmprinter", "LLVMAsmPrinter", true, { "analysis", "binaryformat", "codegen", "core", "debuginfocodeview", "debuginfomsf", "mc", "mcparser", "support", "target" } },
  { "binaryformat", "LLVMBinaryFormat", true, { "support" } },
  { "bitreader", "LLVMBitReader", true, { "core", "support" } },
  { "bitwriter", "LLVMBitWriter", true, { "analysis", "core", "mc", "object", "support" } },
  { "codegen", "LLVMCodeGen", true, { "analysis", "bitreader", "bitwriter", "core", "mc", "profiledata", "scalaropts", "support", "target", "transformutils" } },
  { "core", "LLVMCore", true, { "binaryformat", "support" } },
  { "coroutines", "LLVMCoroutines", true, { "analysis", "core", "ipo", "scalaropts", "support", "transformutils" } },
  { "coverage", "LLVMCoverage", true, { "core", "object", "profiledata", "support" } },
  { "debuginfocodeview", "LLVMDebugInfoCodeView", true, { "support", "debuginfomsf" } },
  { "debuginfodwarf", "LLVMDebugInfoDWARF", true, { "binaryformat", "object", "support" } },
  { "debuginfomsf", "LLVMDebugInfoMSF", true, { "support" } },
  { "debuginfopdb", "LLVMDebugInfoPDB", true, { "object", "support", "debuginfocodeview", "debuginfomsf" } },
  { "demangle", "LLVMDemangle", true, {  } },
  { "dlltooldriver", "LLVMDlltoolDriver", true, { "object", "option", "support" } },
  { "engine", nullptr, true, { "mcjit", "native" } },
  { "executionengine", "LLVMExecutionEngine", true, { "core", "mc", "object", "runtimedyld", "support", "target" } },
  { "globalisel", "LLVMGlobalISel", true, { "analysis", "codegen", "core", "mc", "support", "target", "transformutils" } },
  { "gtest", "gtest", false, { "support" } },
  { "gtest_main", "gtest_main", false, { "gtest" } },
  { "instcombine", "LLVMInstCombine", true, { "analysis", "core", "support", "transformutils" } },
  { "instrumentation", "LLVMInstrumentation", true, { "analysis", "core", "mc", "support", "transformutils", "profiledata" } },
  { "interpreter", "LLVMInterpreter", true, { "codegen", "core", "executionengine", "support" } },
  { "ipo", "LLVMipo", true, { "analysis", "bitreader", "bitwriter", "core", "instcombine", "irreader", "linker", "object", "profiledata", "scalaropts", "support", "transformutils", "vectorize", "instrumentation" } },
  { "irreader", "LLVMIRReader", true, { "asmparser", "bitreader", "core", "support" } },
  { "libdriver", "LLVMLibDriver", true, { "binaryformat", "object", "option", "support" } },
  { "lineeditor", "LLVMLineEditor", true, { "support" } },
  { "linker", "LLVMLinker", true, { "core", "support", "transformutils" } },
  { "lto", "LLVMLTO", true, { "analysis", "bitreader", "bitwriter", "codegen", "core", "ipo", "instcombine", "linker", "mc", "objcarcopts", "object", "passes", "scalaropts", "support", "target", "transformutils" } },
  { "mc", "LLVMMC", true, { "support" } },
  { "mcdisassembler", "LLVMMCDisassembler", true, { "mc", "support" } },
  { "mcjit", "LLVMMCJIT", true, { "core", "executionengine", "object", "runtimedyld", "support", "target" } },
  { "mcparser", "LLVMMCParser", true, { "mc", "support" } },
  { "mirparser", "LLVMMIRParser", true, { "asmparser", "codegen", "core", "mc", "support", "target" } },
  { "native", nullptr, true, { "x86" } },
  { "nativecodegen", nullptr, true, { "x86codegen" } },
  { "objcarcopts", "LLVMObjCARCOpts", true, { "analysis", "core", "support", "transformutils" } },
  { "object", "LLVMObject", true, { "bitreader", "core", "mc", "binaryformat", "mcparser", "support" } },
  { "objectyaml", "LLVMObjectYAML", true, { "support", "debuginfocodeview" } },
  { "option", "LLVMOption", true, { "support" } },
  { "orcjit", "LLVMOrcJIT", true, { "core", "executionengine", "object", "runtimedyld", "support", "transformutils" } },
  { "passes", "LLVMPasses", true, { "analysis", "codegen", "core", "ipo", "instcombine", "scalaropts", "support", "transformutils", "vectorize", "instrumentation" } },
  { "profiledata", "LLVMProfileData", true, { "core", "support" } },
  { "runtimedyld", "LLVMRuntimeDyld", true, { "mc", "object", "support" } },
  { "scalaropts", "LLVMScalarOpts", true, { "analysis", "core", "instcombine", "support", "transformutils" } },
  { "selectiondag", "LLVMSelectionDAG", true, { "analysis", "codegen", "core", "mc", "support", "target", "transformutils" } },
  { "support", "LLVMSupport", true, { "demangle" } },
  { "symbolize", "LLVMSymbolize", true, { "debuginfodwarf", "debuginfopdb", "object", "support" } },
  { "tablegen", "LLVMTableGen", true, { "support" } },
  { "target", "LLVMTarget", true, { "analysis", "core", "mc", "support" } },
  { "testingsupport", "LLVMTestingSupport", false, { "support" } },
  { "transformutils", "LLVMTransformUtils", true, { "analysis", "core", "support" } },
  { "vectorize", "LLVMVectorize", true, { "analysis", "core", "support", "transformutils" } },
  { "x86", nullptr, true, { "x86utils", "x86asmprinter", "x86info", "x86desc", "x86codegen", "x86asmparser", "x86disassembler" } },
  { "x86asmparser", "LLVMX86AsmParser", true, { "mc", "mcparser", "support", "x86desc", "x86info" } },
  { "x86asmprinter", "LLVMX86AsmPrinter", true, { "mc", "support", "x86utils" } },
  { "x86codegen", "LLVMX86CodeGen", true, { "analysis", "asmprinter", "codegen", "core", "mc", "selectiondag", "support", "target", "x86asmprinter", "x86desc", "x86info", "x86utils", "globalisel" } },
  { "x86desc", "LLVMX86Desc", true, { "mc", "mcdisassembler", "object", "support", "x86asmprinter", "x86info" } },
  { "x86disassembler", "LLVMX86Disassembler", true, { "mcdisassembler", "support", "x86info" } },
  { "x86info", "LLVMX86Info", true, { "support" } },
  { "x86utils", "LLVMX86Utils", true, { "core", "support" } },
};
