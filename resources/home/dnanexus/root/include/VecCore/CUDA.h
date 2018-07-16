#ifndef VECCORE_CUDA_H
#define VECCORE_CUDA_H

#if !defined(VECCORE_ENABLE_CUDA)

#define VECCORE_IMPL_NAMESPACE cxx

#define VECCORE_ATT_HOST               /* empty */
#define VECCORE_ATT_DEVICE             /* empty */
#define VECCORE_ATT_HOST_DEVICE        /* empty */
#define VECCORE_ATT_GLOBAL             /* empty */
#define VECCORE_CUDA_ALIGN             /* empty */
#define VECCORE_DECLARE_CUDA(x)        /* empty */
#define VECCORE_DECLARE_CUDA_TYPE(T)   /* empty */
#define VECCORE_DECLARE_CUDA_CLASS(x)  /* empty */
#define VECCORE_DECLARE_CUDA_STRUCT(x) /* empty */
#define VECCORE_DEVICE_CONSTANT

#elif (defined(__CUDACC__) || defined(__NVCC__))

#define VECCORE_IMPL_NAMESPACE cuda

#define VECCORE_CUDA
#ifdef __CUDA_ARCH__
#define VECCORE_CUDA_DEVICE_COMPILATION
#endif

#define VECCORE_ATT_HOST __host__
#define VECCORE_ATT_DEVICE __device__
#define VECCORE_ATT_HOST_DEVICE __host__ __device__
#define VECCORE_ATT_GLOBAL __global__
#define VECCORE_CUDA_ALIGN __align__((64))
#define VECCORE_DECLARE_CUDA(x)          /* empty */
#define VECCORE_DECLARE_CUDA_TYPE(T)     /* empty */
#define VECCORE_DECLARE_CUDA_CLASS(x)    /* empty */
#define VECCORE_DECLARE_CUDA_STRUCT(x)   /* empty */
#define VECCORE_DECLARE_CUDA_TEMPLATE(x) /* empty */
#define VECCORE_DEVICE_CONSTANT __constant__

#else // CUDA enabled, but compiling regular C++ code

#define VECCORE_CUDA_INTERFACE
#define VECCORE_ATT_HOST        /* empty */
#define VECCORE_ATT_DEVICE      /* empty */
#define VECCORE_ATT_HOST_DEVICE /* empty */
#define VECCORE_ATT_GLOBAL      /* empty */
#define VECCORE_CUDA_ALIGN      /* empty */

// Keep the macro compact
// clang-format off

#define VECCORE_CUDA_BASIC_TYPES                                               \
template <typename T> struct CudaTypeTraits;                                   \
template <> struct CudaTypeTraits<Float_s>  { using Type = Float_s;  };        \
template <> struct CudaTypeTraits<Double_s> { using Type = Double_s; };        \
template <> struct CudaTypeTraits<Int8_t>   { using Type = Int8_t;   };        \
template <> struct CudaTypeTraits<Int16_s>  { using Type = Int16_s;  };        \
template <> struct CudaTypeTraits<Int32_s>  { using Type = Int32_s;  };        \
template <> struct CudaTypeTraits<Int64_s>  { using Type = Int64_s;  };        \
template <> struct CudaTypeTraits<Uint8_t>  { using Type = Uint8_t;  };        \
template <> struct CudaTypeTraits<Uint16_t> { using Type = Uint16_t; };        \
template <> struct CudaTypeTraits<Uint32_t> { using Type = Uint32_t; };        \
template <> struct CudaTypeTraits<Uint64_t> { using Type = Uint64_t; };        \
template <typename T> using CudaType = typename CudaTypeTraits<T>::Type;

#define VECCORE_DECLARE_CUDA(T) T; namespace cuda { T; }

#define VECCORE_DECLARE_CUDA_TYPE(T)                                           \
  template <> struct CudaTypeTraits<T> { using Type = cuda::T; };              \

#define VECCORE_DECLARE_CUDA_CLASS(x)                                          \
  VECCORE_DECLARE_CUDA(class x) VECCORE_DECLARE_CUDA_TYPE(x)

#define VECCORE_DECLARE_CUDA_STRUCT(x)                                         \
  VECCORE_DECLARE_CUDA(struct x) VECCORE_DECLARE_CUDA_TYPE(x)

// clang-format on

#endif // defined (VECCORE_ENABLE_CUDA)

#endif
