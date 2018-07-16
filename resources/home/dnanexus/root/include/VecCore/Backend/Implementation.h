#ifndef VECCORE_BACKEND_IMPLEMENTATION_H
#define VECCORE_BACKEND_IMPLEMENTATION_H

#include "Interface.h"
#include "../Limits.h"

#include <algorithm>
#include <type_traits>

namespace vecCore {

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
constexpr Size_s VectorSize()
{
  using V = typename std::decay<T>::type;
  return sizeof(V) / sizeof(Scalar<V>);
}

// Iterators

template <typename T>
struct IteratorImplementation {
  VECCORE_FORCE_INLINE VECCORE_ATT_HOST_DEVICE static Scalar<T> *Begin(T &v)
  {
    Scalar<T> *addr = (Scalar<T> *)(&v);
    return addr;
  }

  VECCORE_FORCE_INLINE VECCORE_ATT_HOST_DEVICE static Scalar<T> *End(T &v)
  {
    Scalar<T> *addr = (Scalar<T> *)(&v);
    return addr + sizeof(v);
  }

  VECCORE_FORCE_INLINE VECCORE_ATT_HOST_DEVICE static Scalar<T> const *Begin(const T &v)
  {
    Scalar<T> const *addr = (Scalar<T> *)(&v);
    return addr;
  }

  VECCORE_FORCE_INLINE VECCORE_ATT_HOST_DEVICE static Scalar<T> const *End(const T &v)
  {
    Scalar<T> const *addr = (Scalar<T> *)(&v);
    return addr + sizeof(v);
  }
};

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
Scalar<T> *Begin(T &v)
{
  return IteratorImplementation<T>::Begin(v);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
Scalar<T> *End(T &v)
{
  return IteratorImplementation<T>::End(v);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
Scalar<T> const *Begin(T const &v)
{
  return IteratorImplementation<T>::Begin(v);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
Scalar<T> const *End(T const &v)
{
  return IteratorImplementation<T>::End(v);
}

// Get/Set

template <typename T>
struct IndexingImplementation {
  VECCORE_FORCE_INLINE VECCORE_ATT_HOST_DEVICE static Scalar<T> Get(const T &v, size_t i) { return *(Begin(v) + i); }

  VECCORE_FORCE_INLINE VECCORE_ATT_HOST_DEVICE static void Set(T &v, size_t i, Scalar<T> const val)
  {
    *(Begin(v) + i) = val;
  }
};

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
Scalar<T> Get(const T &v, size_t i)
{
  return IndexingImplementation<T>::Get(v, i);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
void Set(T &v, size_t i, Scalar<T> const val)
{
  IndexingImplementation<T>::Set(v, i, val);
}

// Load/Store

template <typename T>
struct LoadStoreImplementation {
  template <typename S = Scalar<T>>
  VECCORE_FORCE_INLINE
  VECCORE_ATT_HOST_DEVICE
  static void Load(T &v, S const *ptr)
  {
    for (size_t i = 0; i < VectorSize<T>(); ++i)
      Set(v, i, ptr[i]);
  }

  template <typename S = Scalar<T>>
  VECCORE_FORCE_INLINE
  VECCORE_ATT_HOST_DEVICE
  static void Store(T const &v, S *ptr)
  {
    for (size_t i = 0; i < VectorSize<T>(); ++i)
      ptr[i]      = static_cast<S>(Get(v, i));
  }
};

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
void Load(T &v, Scalar<T> const *ptr)
{
  LoadStoreImplementation<T>::template Load(v, ptr);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
void Store(T const &v, Scalar<T> *ptr)
{
  LoadStoreImplementation<T>::template Store(v, ptr);
}

// Gather/Scatter

template <typename T>
struct GatherScatterImplementation {
  template <typename S = Scalar<T>>
  VECCORE_FORCE_INLINE
  VECCORE_ATT_HOST_DEVICE
  static void Gather(T &v, S const *ptr, Index<T> const &idx)
  {
    for (size_t i = 0; i < VectorSize<T>(); ++i)
      Set(v, i, ptr[Get(idx, i)]);
  }

  template <typename S = Scalar<T>>
  VECCORE_FORCE_INLINE
  VECCORE_ATT_HOST_DEVICE
  static void Scatter(T const &v, S *ptr, Index<T> const &idx)
  {
    for (size_t i = 0; i < VectorSize<T>(); ++i)
      ptr[Get(idx, i)] = Get(v, i);
  }
};

template <typename T, typename S>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T Gather(S const *ptr, Index<T> const &idx)
{
  T v;
  GatherScatterImplementation<T>::template Gather<S>(v, ptr, idx);
  return v;
}

template <typename T, typename S>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
void Scatter(T const &v, S *ptr, Index<T> const &idx)
{
  GatherScatterImplementation<T>::template Scatter<S>(v, ptr, idx);
}

// Masking

template <typename M>
Bool_s MaskFull(const M &mask)
{
  for (size_t i = 0; i < VectorSize<M>(); i++)
    if (Get(mask, i) == false) return false;
  return true;
}

template <typename M>
Bool_s MaskEmpty(const M &mask)
{
  for (size_t i = 0; i < VectorSize<M>(); i++)
    if (Get(mask, i) == true) return false;
  return true;
}

// Split generic scalar/vector implementations to avoid performance loss

template <typename T, Bool_s>
struct GenericMaskingImplementation {
  VECCORE_FORCE_INLINE
  VECCORE_ATT_HOST_DEVICE
  static void Assign(T &dst, Mask<T> const &mask, T const &src)
  {
    for (size_t i = 0; i < VectorSize<T>(); i++)
      if (Get(mask, i)) Set(dst, i, Get(src, i));
  }

  VECCORE_FORCE_INLINE
  VECCORE_ATT_HOST_DEVICE
  static void Blend(T &dst, Mask<T> const &mask, T const &src1, T const &src2)
  {
    for (size_t i = 0; i < VectorSize<T>(); i++)
      Set(dst, i, Get(mask, i) ? Get(src1, i) : Get(src2, i));
  }
};

template <typename T>
struct GenericMaskingImplementation<T, true> {
  VECCORE_FORCE_INLINE
  VECCORE_ATT_HOST_DEVICE
  static void Assign(T &dst, Mask<T> const &mask, T const &src)
  {
    if (mask) dst = src;
  }

  VECCORE_FORCE_INLINE
  VECCORE_ATT_HOST_DEVICE
  static void Blend(T &dst, Mask<T> const &mask, T const &src1, T const &src2) { dst = mask ? src1 : src2; }
};

template <typename T>
struct MaskingImplementation {
  VECCORE_FORCE_INLINE
  VECCORE_ATT_HOST_DEVICE
  static void Assign(T &dst, Mask<T> const &mask, T const &src)
  {
    GenericMaskingImplementation<T, std::is_scalar<T>::value>::Assign(dst, mask, src);
  }

  VECCORE_FORCE_INLINE
  VECCORE_ATT_HOST_DEVICE
  static void Blend(T &dst, Mask<T> const &mask, T const &src1, T const &src2)
  {
    GenericMaskingImplementation<T, std::is_scalar<T>::value>::Blend(dst, mask, src1, src2);
  }
};

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
void MaskedAssign(T &dst, const Mask<T> &mask, const T &src)
{
  MaskingImplementation<T>::Assign(dst, mask, src);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T Blend(const Mask<T> &mask, const T &src1, const T &src2)
{
  T v;
  MaskingImplementation<T>::Blend(v, mask, src1, src2);
  return v;
}

// Miscellaneous

VECCORE_FORCE_INLINE VECCORE_ATT_HOST_DEVICE constexpr Bool_s EarlyReturnAllowed()
{
#ifdef VECCORE_CUDA_DEVICE_COMPILATION
  return false;
#else
  return true;
#endif
}

template <typename T>
VECCORE_FORCE_INLINE VECCORE_ATT_HOST_DEVICE
constexpr Bool_s EarlyReturnMaxLength(T &, size_t n)
{
   return EarlyReturnAllowed() && VectorSize<T>() <= n;
}

// Reduction

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
Scalar<T> ReduceAdd(const T& v)
{
   Scalar<T> result(0);
   for (size_t i = 0; i < VectorSize<T>(); ++i)
      result += Get(v, i);
   return result;
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
Scalar<T> ReduceMin(const T& v)
{
   Scalar<T> result(NumericLimits<Scalar<T>>::Max());
   for (size_t i = 0; i < VectorSize<T>(); ++i)
      result = std::min(result, Get(v, i));
   return result;
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
Scalar<T> ReduceMax(const T& v)
{
   Scalar<T> result(NumericLimits<Scalar<T>>::Lowest());
   for (size_t i = 0; i < VectorSize<T>(); ++i)
      result = std::max(result, Get(v, i));
   return result;
}

template<typename Vout, typename Vin>
Vout Convert(const Vin& v)
{
   Vout out;
   static_assert(VectorSize<Vin>() == VectorSize<Vout>(),
                 "Cannot convert SIMD vectors of different sizes");
   for (size_t i = 0; i < VectorSize<Vin>(); ++i)
      Set(out, i, Get(v, i));
   return out;
}

} // namespace vecCore

#endif
