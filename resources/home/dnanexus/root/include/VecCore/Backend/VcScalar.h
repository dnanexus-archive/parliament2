#ifndef VECCORE_BACKEND_VC_SCALAR_H
#define VECCORE_BACKEND_VC_SCALAR_H

#ifdef VECCORE_ENABLE_VC

#include <Vc/Vc>

namespace vecCore {

template <typename T>
struct TypeTraits<Vc::Scalar::Mask<T>> {
  using IndexType  = size_t;
  using ScalarType = Bool_s;
};

template <typename T>
struct TypeTraits<Vc::Scalar::Vector<T>> {
  using ScalarType = T;
  using MaskType   = typename Vc::Scalar::Vector<T>::MaskType;
  using IndexType  = typename Vc::Scalar::Vector<T>::IndexType;
};

namespace backend {

template <typename T = Real_s>
class VcScalarT {
public:
  using Real_v   = Vc::Scalar::Vector<T>;
  using Float_v  = Vc::Scalar::Vector<Float_s>;
  using Double_v = Vc::Scalar::Vector<Double_s>;

  using Int_v   = Vc::Scalar::Vector<Int_s>;
  using Int16_v = Vc::Scalar::Vector<Int16_s>;
  using Int32_v = Vc::Scalar::Vector<Int32_s>;
  using Int64_v = Vc::Scalar::Vector<Int64_s>;

  using UInt_v   = Vc::Scalar::Vector<UInt_s>;
  using UInt16_v = Vc::Scalar::Vector<UInt16_s>;
  using UInt32_v = Vc::Scalar::Vector<UInt32_s>;
  using UInt64_v = Vc::Scalar::Vector<UInt64_s>;
};

using VcScalar = VcScalarT<>;

#ifdef Vc_IMPL_Scalar
template <typename T>
using VcVectorT = VcScalarT<T>;
using VcVector  = VcScalar;
#endif

} // namespace backend

template <typename T>
VECCORE_FORCE_INLINE
Bool_s MaskEmpty(const Vc::Scalar::Mask<T> &mask)
{
  return mask.isEmpty();
}

template <typename T>
VECCORE_FORCE_INLINE
Bool_s MaskFull(const Vc::Scalar::Mask<T> &mask)
{
  return mask.isFull();
}

template <typename T>
struct IndexingImplementation<Vc::Scalar::Mask<T>> {
  using M = Vc::Scalar::Mask<T>;
  static inline Bool_s Get(const M &mask, size_t i) { return mask[i]; }

  static inline void Set(M &mask, size_t i, const Bool_s val) { mask[i] = val; }
};

template <typename T>
struct MaskingImplementation<Vc::Scalar::Vector<T>> {
  using M = Vc::Scalar::Mask<T>;
  using V = Vc::Scalar::Vector<T>;

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
Vc::Scalar::Vector<T> CopySign(const Vc::Scalar::Vector<T> &x, const Vc::Scalar::Vector<T> &y)
{
  return Vc::copysign(x, y);
}

template <typename T>
VECCORE_FORCE_INLINE
Vc::Scalar::Vector<T> Pow(const Vc::Scalar::Vector<T> &x, const Vc::Scalar::Vector<T> &y)
{
  return std::exp(std::log(x[0]) * y[0]);
}

template <typename T>
VECCORE_FORCE_INLINE
Vc::Scalar::Vector<T> Tan(const Vc::Scalar::Vector<T> &x)
{
  return std::tan(x[0]);
}

template <typename T>
VECCORE_FORCE_INLINE
Vc::Scalar::Mask<T> IsInf(const Vc::Scalar::Vector<T> &x)
{
  return Vc::isinf(x);
}
}

} // namespace vecCore

#endif
#endif
