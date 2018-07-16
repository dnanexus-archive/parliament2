#ifndef VECCORE_BACKEND_UMESIMDARRAY_H
#define VECCORE_BACKEND_UMESIMDARRAY_H

#ifdef VECCORE_ENABLE_UMESIMD

#include <umesimd/UMESimd.h>

namespace vecCore {

namespace backend {

// a UME backend with fixed-size types
template <int N = 16>
class UMESimdArray {
public:
  using Real_v   = UME::SIMD::SIMDVec<Real_s, N>;
  using Float_v  = UME::SIMD::SIMDVec<Float_s, N>;
  using Double_v = UME::SIMD::SIMDVec<Double_s, N>;

  using Int_v   = UME::SIMD::SIMDVec<Int_s, N>;
  using Int16_v = UME::SIMD::SIMDVec<Int16_s, N>;
  using Int32_v = UME::SIMD::SIMDVec<Int32_s, N>;
  using Int64_v = UME::SIMD::SIMDVec<Int64_s, N>;

  using UInt_v   = UME::SIMD::SIMDVec<UInt_s, N>;
  using UInt16_v = UME::SIMD::SIMDVec<UInt16_s, N>;
  using UInt32_v = UME::SIMD::SIMDVec<UInt32_s, N>;
  using UInt64_v = UME::SIMD::SIMDVec<UInt64_s, N>;
};

} // namespace backend

} // namespace vecCore

// bring in common implementation
#include "UMESimdCommon.h"

#endif
#endif
