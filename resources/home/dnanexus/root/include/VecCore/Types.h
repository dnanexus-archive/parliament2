#ifndef VECCORE_TYPES_H
#define VECCORE_TYPES_H

#include <cstddef>
#include <cstdint>

namespace vecCore {

using Bool_s = bool;

using Size_s = size_t;

using Int_s   = int32_t;
using Int16_s = int16_t;
using Int32_s = int32_t;
using Int64_s = int64_t;

using UInt_s   = uint32_t;
using UInt16_s = uint16_t;
using UInt32_s = uint32_t;
using UInt64_s = uint64_t;

using Float_s  = float;
using Double_s = double;

#ifdef VECCORE_SINGLE_PRECISION
using Real_s = Float_s;
#else
using Real_s = Double_s;
#endif
}

#endif
