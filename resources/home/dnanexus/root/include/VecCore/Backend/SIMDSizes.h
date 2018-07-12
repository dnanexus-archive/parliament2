#ifndef VECCORE_SIMD_SIZES_H
#define VECCORE_SIMD_SIZES_H

namespace vecCore {

// traits to choose a default vector size depending on the architecture
// TODO: this has to be completed for types and architectures
// TODO: we may replace this by calculating from compiler types ( if this is compiler-portable )
template <typename T>
constexpr size_t SIMDWidth()
{
  return 1;
}
#ifdef __AVX512__
template <>
constexpr size_t SIMDWidth<Double_s>()
{
  return 8;
}
template <>
constexpr size_t SIMDWidth<Float_s>()
{
  return 16;
}
template <>
constexpr size_t SIMDWidth<UInt32_s>()
{
  return 16;
}
template <>
constexpr size_t SIMDWidth<Int32_s>()
{
  return 16;
}
template <>
constexpr size_t SIMDWidth<UInt16_s>()
{
  return 32;
}
template <>
constexpr size_t SIMDWidth<Int16_s>()
{
  return 32;
}
#elif __AVX2__
template <>
constexpr size_t SIMDWidth<Double_s>()
{
  return 4;
}
template <>
constexpr size_t SIMDWidth<Float_s>()
{
  return 8;
}
template <>
constexpr size_t SIMDWidth<UInt32_s>()
{
  return 8;
}
template <>
constexpr size_t SIMDWidth<Int32_s>()
{
  return 8;
}
template <>
constexpr size_t SIMDWidth<UInt16_s>()
{
  return 16;
}
template <>
constexpr size_t SIMDWidth<Int16_s>()
{
  return 16;
}
#elif __AVX__
template <>
constexpr size_t SIMDWidth<Double_s>()
{
  return 4;
}
template <>
constexpr size_t SIMDWidth<Float_s>()
{
  return 8;
}
template <>
constexpr size_t SIMDWidth<UInt32_s>()
{
  return 4;
}
template <>
constexpr size_t SIMDWidth<Int32_s>()
{
  return 4;
}
template <>
constexpr size_t SIMDWidth<UInt16_s>()
{
  return 16;
}
template <>
constexpr size_t SIMDWidth<Int16_s>()
{
  return 16;
}
#elif __SSE__
template <>
constexpr size_t SIMDWidth<Double_s>()
{
  return 2;
}
template <>
constexpr size_t SIMDWidth<Float_s>()
{
  return 4;
}
template <>
constexpr size_t SIMDWidth<UInt32_s>()
{
  return 4;
}
template <>
constexpr size_t SIMDWidth<Int32_s>()
{
  return 4;
}
template <>
constexpr size_t SIMDWidth<UInt16_s>()
{
  return 8;
}
template <>
constexpr size_t SIMDWidth<Int16_s>()
{
  return 8;
}
#endif
}

#endif
