#ifndef VECCORE_SIMD_H
#define VECCORE_SIMD_H

#if defined(__i386__) || defined(__x86_64__)
#include <x86intrin.h>
#endif

#if defined(__AVX512F__) || defined(__MIC__)
#define VECCORE_SIMD_ALIGN 64
#elif defined(__AVX__)
#define VECCORE_SIMD_ALIGN 32
#else
#define VECCORE_SIMD_ALIGN 16
#endif

#endif
