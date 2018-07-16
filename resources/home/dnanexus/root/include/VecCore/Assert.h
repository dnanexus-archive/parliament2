#ifndef VECCORE_ASSERT_H
#define VECCORE_ASSERT_H

#if !defined(__NVCC__)
#include <cassert>
#else

// NVCC sometimes cannot process plain assert() from <cassert>, so
// we need to provide our own implementation that works around the bug
// by avoiding the __PRETTY_FUNCTION__ macro where it causes problems.
// A bug for this has been filed by Philippe Canal at the link below:
// https://developer.nvidia.com/nvbugs/cuda/edit/1729798

#ifdef assert
#undef assert
#endif

#ifdef NDEBUG
#define assert(x)
#else

#include <cstdio>

#ifndef __CUDA_ARCH__
#define assert(x)                                                                 \
  do {                                                                            \
    if (!(x)) {                                                                   \
      fprintf(stderr, "%s:%d: Assertion failed: '%s'\n", __FILE__, __LINE__, #x); \
      abort();                                                                    \
    }                                                                             \
  } while (0)
#else
#define assert(x)                                                                                  \
  do {                                                                                             \
    if (!(x)) {                                                                                    \
      printf("%s:%d:\n%s: Assertion failed: '%s'\n", __FILE__, __LINE__, __PRETTY_FUNCTION__, #x); \
      __syncthreads();                                                                             \
      asm("trap;");                                                                                \
    }                                                                                              \
  } while (0)
#endif // ifndef __CUDA_ARCH__

#endif // ifdef NDEBUG

#endif // if !defined(__NVCC__)

#endif
