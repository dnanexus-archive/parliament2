#ifndef VECCORE_BACKEND_VC_SIMDARRAY_H
#define VECCORE_BACKEND_VC_SIMDARRAY_H

#ifdef VECCORE_ENABLE_VC

#include <Vc/Vc>

namespace vecCore {

template <typename T, size_t N>
struct TypeTraits<Vc::SimdMaskArray<T, N>> {
  using ScalarType = Bool_s;
  using IndexType  = size_t;
};

template <typename T, size_t N>
struct TypeTraits<Vc::SimdArray<T, N>> {
  using ScalarType = T;
  using MaskType   = typename Vc::SimdArray<T, N>::MaskType;
  using IndexType  = typename Vc::SimdArray<T, N>::IndexType;
};

namespace backend {

template <size_t N = 16>
class VcSimdArray {
public:
  using Real_v   = Vc::SimdArray<Real_s, N>;
  using Float_v  = Vc::SimdArray<Float_s, N>;
  using Double_v = Vc::SimdArray<Double_s, N>;

  using Int_v   = Vc::SimdArray<Int_s, N>;
  using Int16_v = Vc::SimdArray<Int16_s, N>;
  using Int32_v = Vc::SimdArray<Int32_s, N>;
  using Int64_v = Vc::SimdArray<Int64_s, N>;

  using UInt_v   = Vc::SimdArray<UInt_s, N>;
  using UInt16_v = Vc::SimdArray<UInt16_s, N>;
  using UInt32_v = Vc::SimdArray<UInt32_s, N>;
  using UInt64_v = Vc::SimdArray<UInt64_s, N>;
};

} // namespace backend

template <typename T, size_t N>
VECCORE_FORCE_INLINE
Bool_s MaskEmpty(const Vc::SimdMaskArray<T, N> &mask)
{
  return mask.isEmpty();
}

template <typename T, size_t N>
VECCORE_FORCE_INLINE
Bool_s MaskFull(const Vc::SimdMaskArray<T, N> &mask)
{
  return mask.isFull();
}

template <typename T, size_t N>
struct IndexingImplementation<Vc::SimdMaskArray<T, N>> {
  using M = Vc::SimdMaskArray<T, N>;
  static inline Bool_s Get(const M &mask, size_t i) { return mask[i]; }

  static inline void Set(M &mask, size_t i, const Bool_s val) { mask[i] = val; }
};

template <typename T, size_t N>
struct LoadStoreImplementation<Vc::SimdMaskArray<T, N>> {
  using M = Vc::SimdMaskArray<T, N>;

  template <typename S = Scalar<T>>
  static inline void Load(M &mask, Bool_s const *ptr)
  {
    mask.load(ptr);
  }

  template <typename S = Scalar<T>>
  static inline void Store(M const &mask, S *ptr)
  {
    mask.store(ptr);
  }
};

template <typename T, size_t N>
struct MaskingImplementation<Vc::SimdArray<T, N>> {
  using V = Vc::SimdArray<T, N>;
  using M = Vc::SimdMaskArray<T, N>;

  static inline void Assign(V &dst, M const &mask, V const &src) { dst(mask) = src; }

  static inline void Blend(V &dst, M const &mask, V const &src1, V const &src2)
  {
    dst       = src2;
    dst(mask) = src1;
  }
};

namespace math {

template <typename T, size_t N>
VECCORE_FORCE_INLINE
Vc::SimdArray<T, N> CopySign(const Vc::SimdArray<T, N> &x, const Vc::SimdArray<T, N> &y)
{
  return Vc::copysign(x, y);
}

template <typename T, size_t N>
VECCORE_FORCE_INLINE
Vc::SimdArray<T, N> Pow(const Vc::SimdArray<T, N> &x, const Vc::SimdArray<T, N> &y)
{
  return Vc::exp(Vc::log(x) * y);
}

template <typename T, size_t N>
VECCORE_FORCE_INLINE
Vc::SimdArray<T, N> Tan(const Vc::SimdArray<T, N> &x)
{
  Vc::SimdArray<T, N> s, c;
  Vc::sincos(x, &s, &c);
  return s / c;
}

template <typename T, size_t N>
VECCORE_FORCE_INLINE
Vc::SimdMaskArray<T, N> IsInf(const Vc::SimdArray<T, N> &x)
{
  return Vc::isinf(x);
}
}

} // namespace vecCore

#endif
#endif
