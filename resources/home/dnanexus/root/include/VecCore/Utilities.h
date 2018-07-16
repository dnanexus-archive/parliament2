#ifndef VECCORE_UTILITIES_H
#define VECCORE_UTILITIES_H

#include <cstdlib>

namespace vecCore {

inline void *AlignedAlloc(size_t alignment, size_t size)
{
  void *ptr = nullptr;

  if (posix_memalign(&ptr, alignment, size) == 0)
     return ptr;

  return nullptr;
}

inline void AlignedFree(void *ptr)
{
  free(ptr);
}
}

#endif
