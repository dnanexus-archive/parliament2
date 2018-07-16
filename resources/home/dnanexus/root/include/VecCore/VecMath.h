#ifndef VECCORE_MATH_H
#define VECCORE_MATH_H

#include <cmath>

namespace vecCore {
namespace math {

// Abs, Min, Max, Sign

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T Abs(const T &x)
{
  return std::abs(x);
}

template <class T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T Min(const T &a, const T &b)
{
  return Blend(a < b, a, b);
}

template <class T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T Max(const T &a, const T &b)
{
  return Blend(a > b, a, b);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T Min(const T &a, const T &b, const T &c)
{
  return Min(a, Min(b, c));
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T Max(const T &a, const T &b, const T &c)
{
  return Max(a, Max(b, c));
}

template <typename T, template <typename> class Wrapper>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
Wrapper<T> Min(const Wrapper<T> &a, const Wrapper<T> &b)
{
  return Blend(a < b, a, b);
}

template <typename T, template <typename> class Wrapper>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
Wrapper<T> Max(const Wrapper<T> &a, const Wrapper<T> &b)
{
  return Blend(a > b, a, b);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T CopySign(const T &x, const T &y)
{
  return std::copysign(x, y);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T Sign(const T &x)
{
  return CopySign(T(1), x);
}

// Trigonometric Functions

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T Sin(const T &x)
{
  return std::sin(x);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T Cos(const T &x)
{
  return std::cos(x);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
void SinCos(const T &x, T *s, T *c)
{
  sincos(x, s, c);
}

#if defined(__APPLE__) && !defined(NVCC)
VECCORE_FORCE_INLINE
void sincosf(const float &x, float *s, float *c)
{
  __sincosf(x, s, c);
}

VECCORE_FORCE_INLINE
void sincos(const double &x, double *s, double *c)
{
  __sincos(x, s, c);
}
#endif

template <>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
void SinCos(const Float_s &x, Float_s *s, Float_s *c)
{
  sincosf(x, s, c);
}

template <>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
void SinCos(const Double_s &x, Double_s *s, Double_s *c)
{
  sincos(x, s, c);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T Tan(const T &x)
{
  return std::tan(x);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T ASin(const T &x)
{
  return std::asin(x);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T ACos(const T &x)
{
  return std::acos(x);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T ATan(const T &x)
{
  return std::atan(x);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T ATan2(const T &x, const T &y)
{
  return std::atan2(x, y);
}

// Hyperbolic Functions

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T Sinh(const T &x)
{
  return std::sinh(x);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T Cosh(const T &x)
{
  return std::cosh(x);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T Tanh(const T &x)
{
  return std::tanh(x);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T ASinh(const T &x)
{
  return std::asinh(x);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T ACosh(const T &x)
{
  return std::acosh(x);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T ATanh(const T &x)
{
  return std::atanh(x);
}

// Exponential and Logarithmic Functions

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T Exp(const T &x)
{
  return std::exp(x);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T Frexp(const T &x, int *exp)
{
  return std::frexp(x, exp);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T Ldexp(const T &x, int exp)
{
  return std::ldexp(x, exp);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T Log(const T &x)
{
  return std::log(x);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T Log10(const T &x)
{
  return std::log10(x);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T Modf(const T &x, T *intpart)
{
  return std::modf(x, intpart);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T Exp2(const T &x)
{
  return std::exp2(x);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T Expm1(const T &x)
{
  return std::expm1(x);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T Ilogb(const T &x)
{
  return std::ilogb(x);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T Log1p(const T &x)
{
  return std::log1p(x);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T Log2(const T &x)
{
  return std::log2(x);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T Logb(const T &x)
{
  return std::logb(x);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T Scalbn(const T &x, int n)
{
  return std::scalbn(x, n);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T Scalbln(const T &x, long int n)
{
  return std::scalbln(x, n);
}

// Power Functions

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T Sqrt(const T &x)
{
  return std::sqrt(x);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T Cbrt(const T &x)
{
  return std::cbrt(x);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T Pow(const T &x, const T &y)
{
  return std::pow(x, y);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T Hypot(const T &x, const T &y)
{
  return std::hypot(x, y);
}

// Rounding and Remainder Functions

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T Ceil(const T &x)
{
  return std::ceil(x);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T Floor(const T &x)
{
  return std::floor(x);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T Fmod(const T &x, const T &y)
{
  return std::fmod(x, y);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T Trunc(const T &x)
{
  return std::trunc(x);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
T Round(const T &x)
{
  return std::round(x);
}

// Miscellaneous Utilities

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
Mask<T> IsInf(const T &x)
{
#ifndef VECCORE_CUDA
  using std::isinf;
#endif
  return isinf(x);
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
constexpr T Deg(const T &x)
{
  return (x * T(180.0 / M_PI));
}

template <typename T>
VECCORE_FORCE_INLINE
VECCORE_ATT_HOST_DEVICE
constexpr T Rad(const T &x)
{
  return (x * T(M_PI / 180.0));
}

} // namespace math
} // namespace vecCore

#endif
