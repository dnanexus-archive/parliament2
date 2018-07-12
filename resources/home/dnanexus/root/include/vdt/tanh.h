/*
 * tanh.h
 * The basic idea is to exploit Pade polynomials.
 * Implemented by Manuel Schiller for LHCb.
 * 
 *  Created on: Sep 23, 2017
 *      Author: Paul Seyfert, Manuel Schiller
 */

/* 
 * VDT is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser Public License for more details.
 * 
 * You should have received a copy of the GNU Lesser Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#ifndef TANH_H_
#define TANH_H_

#include "vdtcore_common.h"

namespace vdt{




/// Fast tanh implementation double precision
inline double fast_tanh(double x){
	// for very large |x| > 20, tanh(x) is x/|x| anyway (at least to double
	// precision)
	//
	// NB: branch-free code takes longer to execute
	if (std::abs(x) > 20.) return std::copysign(1., x);
	// strategy for large arguments: tanh(2x) = 2 tanh(x)/(1 + tanh^2(x))
	// idea is to use this "argument halving" a couple of times, and use a
	// very short Padé approximation for the rest of the way
	const auto xx = x * 0.125;
	const auto xx2 = xx * xx;
	const auto numer = 135135 + xx2 * (17325 + xx2 * ( 378 + xx2 *  1));
	const auto denom = 135135 + xx2 * (62370 + xx2 * (3150 + xx2 * 28));

	auto tanh = xx * numer / denom;
	tanh = 2 * tanh / (tanh * tanh + 1);
	tanh = 2 * tanh / (tanh * tanh + 1);
	return 2 * tanh / (tanh * tanh + 1);
}

//------------------------------------------------------------------------------
/// Fast tanh implementation single precision
inline float fast_tanhf( float x ) {
	// same strategy as double version above, but even shorter Padé
	// approximation is sufficient for float
	//
	// NB: branch-free code takes longer to execute
	if (std::abs(x) > 9.1f) return std::copysign(1.f, x);
	const auto xx = x * 0.125f;
	const auto xx2 = xx * xx;
	auto tanh = xx * (xx2 + 15) / (6 * xx2 + 15);
	tanh = 2 * tanh / (tanh * tanh + 1);
	tanh = 2 * tanh / (tanh * tanh + 1);
	return 2 * tanh / (tanh * tanh + 1);
}

//------------------------------------------------------------------------------
// Vector signatures

void tanhv(const uint32_t size, double const * __restrict__ iarray, double* __restrict__ oarray);
void fast_tanhv(const uint32_t size, double const * __restrict__ iarray, double* __restrict__ oarray);
void tanhfv(const uint32_t size, float const * __restrict__ iarray, float* __restrict__ oarray);
void fast_tanhfv(const uint32_t size, float const * __restrict__ iarray, float* __restrict__ oarray);

}// end of vdt

#endif // end of tanh
