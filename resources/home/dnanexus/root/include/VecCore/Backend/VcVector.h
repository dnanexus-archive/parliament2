#ifndef VECCORE_BACKEND_VC_VECTOR_H
#define VECCORE_BACKEND_VC_VECTOR_H

#ifdef VECCORE_ENABLE_VC

#include <Vc/Vc>

#ifndef Vc_IMPL_Scalar

namespace vecCore {

template <typename T>
struct TypeTraits<Vc::Mask<T>> {
  using IndexType  = size_t;
  using ScalarType = Bool_s;
};

template <typename T>
struct TypeTraits<Vc::Vector<T>> {
  using ScalarType = T;
  using MaskType   = typename Vc::Vector<T>::MaskType;
  using IndexType  = typename Vc::Vector<T>::IndexType;
};

namespace backend {

template <typename T = Real_s>
class VcVectorT {
public:
  using Real_v   = Vc::Vector<T>;
  using Float_v  = Vc::Vector<Float_s>;
  using Double_v = Vc::Vector<Double_s>;

  using Int_v   = Vc::Vector<Int_s>;
  using Int16_v = Vc::Vector<Int16_s>;
  using Int32_v = Vc::Vector<Int32_s>;
  using Int64_v = Vc::Vector<Int64_s>;

  using UInt_v   = Vc::Vector<UInt_s>;
  using UInt16_v = Vc::Vector<UInt16_s>;
  using UInt32_v = Vc::Vector<UInt32_s>;
  using UInt64_v = Vc::Vector<UInt64_s>;
};

using VcVector = VcVectorT<>;

} // namespace backend

template <typename T>
VECCORE_FORCE_INLINE
Bool_s MaskEmpty(const Vc::Mask<T> &mask)
{
  return mask.isEmpty();
}

template <typename T>
VECCORE_FORCE_INLINE
Bool_s MaskFull(const Vc::Mask<T> &mask)
{
  return mask.isFull();
}

template <typename T>
struct IndexingImplementation<Vc::Mask<T>> {
  using M = Vc::Mask<T>;
  static inline Bool_s Get(const M &mask, size_t i) { return mask[i]; }

  static inline void Set(M &mask, size_t i, const Bool_s val) { mask[i] = val; }
};

template <typename T>
struct LoadStoreImplementation<Vc::Mask<T>> {
  using M = Vc::Mask<T>;

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

template <typename T>
struct MaskingImplementation<Vc::Vector<T>> {
  using M = Vc::Mask<T>;
  using V = Vc::Vector<T>;

  static inline void Assign(V &dst, M const &mask, V const &src) { dst(mask) = src; }

  static inline void Blend(V &dst, M const &mask, V const &src1, V const src2)
  {
    dst       = src2;
    dst(mask) = src1;
  }
};

namespace math {

template <typename T>
VECCORE_FORCE_INLINE
Vc::Vector<T> CopySign(const Vc::Vector<T> &x, const Vc::Vector<T> &y)
{
  return Vc::copysign(x, y);
}

template <typename T>
VECCORE_FORCE_INLINE
Vc::Vector<T> Pow(const Vc::Vector<T> &x, const Vc::Vector<T> &y)
{
  return Vc::exp(Vc::log(x) * y);
}

template <typename T>
VECCORE_FORCE_INLINE
Vc::Vector<T> Tan(const Vc::Vector<T> &x)
{
  Vc::Vector<T> s, c;
  Vc::sincos(x, &s, &c);
  return s / c;
}

template <typename T>
VECCORE_FORCE_INLINE
Vc::Mask<T> IsInf(const Vc::Vector<T> &x)
{
  return Vc::isinf(x);
}
}

} // namespace vecCore

#endif
#endif
#endif
