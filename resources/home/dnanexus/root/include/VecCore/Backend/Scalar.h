#ifndef VECCORE_BACKEND_SCALAR_H
#define VECCORE_BACKEND_SCALAR_H

#include "Interface.h"
#include "Implementation.h"

namespace vecCore {

template <typename T>
struct TypeTraits {
  using ScalarType = T;
  using MaskType   = Bool_s;
  using IndexType  = Size_s;
};

namespace backend {

template <typename T = Real_s>
class ScalarT {
public:
  using Real_v   = T;
  using Float_v  = Float_s;
  using Double_v = Double_s;

  using Int_v   = Int_s;
  using Int16_v = Int16_s;
  using Int32_v = Int32_s;
  using Int64_v = Int64_s;

  using UInt_v   = UInt_s;
  using UInt16_v = UInt16_s;
  using UInt32_v = UInt32_s;
  using UInt64_v = UInt64_s;
};

using Scalar = ScalarT<>;

} // namespace backend

template <>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
Bool_s MaskEmpty<Bool_s>(const Bool_s &mask)
{
  return !mask;
}

template <>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
Bool_s MaskFull<Bool_s>(const Bool_s &mask)
{
  return mask;
}

} // namespace vecCore

#endif
