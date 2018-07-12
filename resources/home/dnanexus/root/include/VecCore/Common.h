#ifndef VECCORE_COMMON_H
#define VECCORE_COMMON_H

#include "CUDA.h"
#include "SIMD.h"

#ifndef VECCORE_NO_FORCED_INLINING
#define VECCORE_FORCE_NOINLINE __attribute__((noinline))
#define VECCORE_FORCE_INLINE inline __attribute__((always_inline))
#else
#define VECCORE_FORCE_NOINLINE
#define VECCORE_FORCE_INLINE
#endif

#endif
