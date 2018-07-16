#ifndef VECCORE_LIMITS_H
#define VECCORE_LIMITS_H

#include "Backend/Interface.h"

#include <cfloat>
#include <climits>
#include <cstdint>
#include <cmath>

namespace vecCore {

template <typename T>
struct NumericLimits {
  using ScalarT = Scalar<T>;

  static constexpr T Min() noexcept { return T(NumericLimits<ScalarT>::Min()); }
  static constexpr T Max() noexcept { return T(NumericLimits<ScalarT>::Max()); }

  static constexpr T Lowest() noexcept { return T(NumericLimits<ScalarT>::Lowest()); }
  static constexpr T Highest() noexcept { return T(NumericLimits<ScalarT>::Highest()); }

  static constexpr T Epsilon() noexcept { return T(NumericLimits<ScalarT>::Epsilon()); }
  static constexpr T Infinity() noexcept { return T(NumericLimits<ScalarT>::Infinity()); }
};

template <>
struct NumericLimits<bool> {
  VECCORE_ATT_HOST_DEVICE static constexpr bool Min() { return false; }
  VECCORE_ATT_HOST_DEVICE static constexpr bool Max() { return true; }
};

template <>
struct NumericLimits<int8_t> {
  VECCORE_ATT_HOST_DEVICE static constexpr int8_t Min() { return INT8_MIN; }
  VECCORE_ATT_HOST_DEVICE static constexpr int8_t Max() { return INT8_MAX; }
  VECCORE_ATT_HOST_DEVICE static constexpr int8_t Lowest() { return INT8_MIN; }
  VECCORE_ATT_HOST_DEVICE static constexpr int8_t Highest() { return INT8_MAX; }
};

template <>
struct NumericLimits<uint8_t> {
  VECCORE_ATT_HOST_DEVICE static constexpr uint8_t Min() { return 0; }
  VECCORE_ATT_HOST_DEVICE static constexpr uint8_t Max() { return UINT8_MAX; }
  VECCORE_ATT_HOST_DEVICE static constexpr uint8_t Lowest() { return 0; }
  VECCORE_ATT_HOST_DEVICE static constexpr uint8_t Highest() { return UINT8_MAX; }
};

template <>
struct NumericLimits<int16_t> {
  VECCORE_ATT_HOST_DEVICE static constexpr int16_t Min() { return INT16_MIN; }
  VECCORE_ATT_HOST_DEVICE static constexpr int16_t Max() { return INT16_MAX; }
  VECCORE_ATT_HOST_DEVICE static constexpr int16_t Lowest() { return INT16_MIN; }
  VECCORE_ATT_HOST_DEVICE static constexpr int16_t Highest() { return INT16_MAX; }
};

template <>
struct NumericLimits<uint16_t> {
  VECCORE_ATT_HOST_DEVICE static constexpr uint16_t Min() { return 0; }
  VECCORE_ATT_HOST_DEVICE static constexpr uint16_t Max() { return UINT16_MAX; }
  VECCORE_ATT_HOST_DEVICE static constexpr uint16_t Lowest() { return 0; }
  VECCORE_ATT_HOST_DEVICE static constexpr uint16_t Highest() { return UINT16_MAX; }
};

template <>
struct NumericLimits<int32_t> {
  VECCORE_ATT_HOST_DEVICE static constexpr int32_t Min() { return INT32_MIN; }
  VECCORE_ATT_HOST_DEVICE static constexpr int32_t Max() { return INT32_MAX; }
  VECCORE_ATT_HOST_DEVICE static constexpr int32_t Lowest() { return INT32_MIN; }
  VECCORE_ATT_HOST_DEVICE static constexpr int32_t Highest() { return INT32_MAX; }
};

template <>
struct NumericLimits<uint32_t> {
  VECCORE_ATT_HOST_DEVICE static constexpr uint32_t Min() { return 0; }
  VECCORE_ATT_HOST_DEVICE static constexpr uint32_t Max() { return UINT32_MAX; }
  VECCORE_ATT_HOST_DEVICE static constexpr uint32_t Lowest() { return 0; }
  VECCORE_ATT_HOST_DEVICE static constexpr uint32_t Highest() { return UINT32_MAX; }
};

template <>
struct NumericLimits<int64_t> {
  VECCORE_ATT_HOST_DEVICE static constexpr int64_t Min() { return INT64_MIN; }
  VECCORE_ATT_HOST_DEVICE static constexpr int64_t Max() { return INT64_MAX; }
  VECCORE_ATT_HOST_DEVICE static constexpr int64_t Lowest() { return INT64_MIN; }
  VECCORE_ATT_HOST_DEVICE static constexpr int64_t Highest() { return INT64_MAX; }
};

template <>
struct NumericLimits<uint64_t> {
  VECCORE_ATT_HOST_DEVICE static constexpr uint64_t Min() { return 0; }
  VECCORE_ATT_HOST_DEVICE static constexpr uint64_t Max() { return UINT64_MAX; }
  VECCORE_ATT_HOST_DEVICE static constexpr uint64_t Lowest() { return 0; }
  VECCORE_ATT_HOST_DEVICE static constexpr uint64_t Highest() { return UINT64_MAX; }
};

template <>
struct NumericLimits<float> {
  VECCORE_ATT_HOST_DEVICE static constexpr float Min() { return FLT_MIN; }
  VECCORE_ATT_HOST_DEVICE static constexpr float Max() { return FLT_MAX; }
  VECCORE_ATT_HOST_DEVICE static constexpr float Lowest() { return -FLT_MAX; }
  VECCORE_ATT_HOST_DEVICE static constexpr float Highest() { return FLT_MAX; }
  VECCORE_ATT_HOST_DEVICE static constexpr float Epsilon() { return FLT_EPSILON; }
  VECCORE_ATT_HOST_DEVICE static constexpr float Infinity() noexcept { return HUGE_VALF; }
};

template <>
struct NumericLimits<double> {
  VECCORE_ATT_HOST_DEVICE static constexpr double Min() { return DBL_MIN; }
  VECCORE_ATT_HOST_DEVICE static constexpr double Max() { return DBL_MAX; }
  VECCORE_ATT_HOST_DEVICE static constexpr double Lowest() { return -DBL_MAX; }
  VECCORE_ATT_HOST_DEVICE static constexpr double Highest() { return DBL_MAX; }
  VECCORE_ATT_HOST_DEVICE static constexpr double Epsilon() { return DBL_EPSILON; }
  VECCORE_ATT_HOST_DEVICE static constexpr double Infinity() noexcept { return HUGE_VAL; }
};

} // namespace vecCore

#endif
