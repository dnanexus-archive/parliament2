// internal header; common parts to multiple UMESIMD backends
#ifndef VECCORE_UMESIMDCOMMON_H
#define VECCORE_UMESIMDCOMMON_H

namespace vecCore {

// type traits for UME::SIMD

template <uint32_t N>
struct TypeTraits<UME::SIMD::SIMDVecMask<N>> {
  using MaskType   = typename UME::SIMD::SIMDVecMask<N>;
  using IndexType  = int;
  using ScalarType = Bool_s;
};

template <typename T, uint32_t N>
struct TypeTraits<UME::SIMD::SIMDVec_f<T, N>> {
  using ScalarType = T;
  using MaskType   = typename UME::SIMD::SIMDVecMask<N>;
  using IndexType  = typename UME::SIMD::SIMDVec_u<uint32_t, N>;
};

template <typename T, uint32_t N>
struct TypeTraits<UME::SIMD::SIMDVec_i<T, N>> {
  using ScalarType = T;
  using MaskType   = typename UME::SIMD::SIMDVecMask<N>;
  using IndexType  = typename UME::SIMD::SIMDVec_u<uint32_t, N>;
};

template <typename T, uint32_t N>
struct TypeTraits<UME::SIMD::SIMDVec_u<T, N>> {
  using ScalarType = T;
  using MaskType   = typename UME::SIMD::SIMDVecMask<N>;
  using IndexType  = typename UME::SIMD::SIMDVec_u<uint32_t, N>;
};

// backend functions for UME::SIMD

template <uint32_t N>
VECCORE_FORCE_INLINE
Bool_s MaskFull(const UME::SIMD::SIMDVecMask<N> &cond)
{
  return cond.hland();
}

template <uint32_t N>
VECCORE_FORCE_INLINE
Bool_s MaskEmpty(const UME::SIMD::SIMDVecMask<N> &cond)
{
  return !cond.hlor();
}

template <uint32_t N>
struct IndexingImplementation<UME::SIMD::SIMDVecMask<N>> {
  using M = UME::SIMD::SIMDVecMask<N>;

  VECCORE_FORCE_INLINE VECCORE_ATT_HOST_DEVICE static Bool_s Get(const M &mask, int i) { return mask[i]; }

  VECCORE_FORCE_INLINE VECCORE_ATT_HOST_DEVICE static void Set(M &mask, int i, const Bool_s val)
  {
    mask.insert(i, val);
  }
};

template <uint32_t N>
struct LoadStoreImplementation<UME::SIMD::SIMDVecMask<N>> {
  using M = UME::SIMD::SIMDVecMask<N>;

  template <typename S = Scalar<M>>
  static inline void Load(M &mask, S const *ptr)
  {
    mask.load(ptr);
  }

  template <typename S = Scalar<M>>
  static inline void Store(M const &mask, S *ptr)
  {
    mask.store(ptr);
  }
};

template <typename T, uint32_t N>
struct MaskingImplementation<UME::SIMD::SIMDVec_f<T, N>> {
  using V = UME::SIMD::SIMDVec_f<T, N>;
  using M = UME::SIMD::SIMDVecMask<N>;

  static inline void Assign(V &dst, M const &mask, V const &src) { dst.assign(mask, src); }

  static inline void Blend(V &dst, M const &mask, V const &src1, V const &src2) { dst = src2.blend(mask, src1); }
};

template <typename T, uint32_t N>
struct MaskingImplementation<UME::SIMD::SIMDVec_i<T, N>> {
  using V = UME::SIMD::SIMDVec_i<T, N>;
  using M = UME::SIMD::SIMDVecMask<N>;

  static inline void Assign(V &dst, M const &mask, V const &src) { dst.assign(mask, src); }

  static inline void Blend(V &dst, M const &mask, V const &src1, V const &src2) { dst = src2.blend(mask, src1); }
};

template <typename T, uint32_t N>
struct MaskingImplementation<UME::SIMD::SIMDVec_u<T, N>> {
  using V = UME::SIMD::SIMDVec_u<T, N>;
  using M = UME::SIMD::SIMDVecMask<N>;

  static inline void Assign(V &dst, M const &mask, V const &src) { dst.assign(mask, src); }

  static inline void Blend(V &dst, M const &mask, V const &src1, V const &src2) { dst = src2.blend(mask, src1); }
};

namespace math {

template <typename T, uint32_t N>
VECCORE_FORCE_INLINE
UME::SIMD::SIMDVec_f<T, N> CopySign(const UME::SIMD::SIMDVec_f<T, N> &x, const UME::SIMD::SIMDVec_f<T, N> &y)
{
  return x.copysign(y);
}

template <typename T, uint32_t N>
VECCORE_FORCE_INLINE
void SinCos(const UME::SIMD::SIMDVec_f<T, N> &x, UME::SIMD::SIMDVec_f<T, N> *s, UME::SIMD::SIMDVec_f<T, N> *c)
{
  *s = x.sin();
  *c = x.cos();
}

template <typename T, uint32_t N>
VECCORE_FORCE_INLINE
UME::SIMD::SIMDVec_f<T, N> Pow(const UME::SIMD::SIMDVec_f<T, N> &x, const UME::SIMD::SIMDVec_f<T, N> &y)
{
  return (x.log() * y).exp();
}

#define UMESIMD_REAL_FUNC(f, name)                                                                \
  template <typename T, uint32_t N>                                                               \
  VECCORE_FORCE_INLINE typename UME::SIMD::SIMDVec_f<T, N> f(const UME::SIMD::SIMDVec_f<T, N> &x) \
  {                                                                                               \
    return x.name();                                                                              \
  }

UMESIMD_REAL_FUNC(Abs, abs)
UMESIMD_REAL_FUNC(Exp, exp)
UMESIMD_REAL_FUNC(Log, log)
UMESIMD_REAL_FUNC(Sin, sin)
UMESIMD_REAL_FUNC(Cos, cos)
UMESIMD_REAL_FUNC(Tan, tan)
UMESIMD_REAL_FUNC(ATan, atan)
UMESIMD_REAL_FUNC(Sqrt, sqrt)
UMESIMD_REAL_FUNC(Round, round)
UMESIMD_REAL_FUNC(Floor, floor)
UMESIMD_REAL_FUNC(Ceil, ceil)

#undef UMESIMD_REAL_FUNC

template <typename T, uint32_t N>
VECCORE_FORCE_INLINE
UME::SIMD::SIMDVecMask<N> IsInf(const UME::SIMD::SIMDVec_f<T, N> &x)
{
  return x.isinf();
}

} // end namespace math
} // end namespace vecCore

#endif
