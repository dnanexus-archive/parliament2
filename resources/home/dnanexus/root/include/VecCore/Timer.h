#ifndef VECCORE_TIMER_H
#define VECCORE_TIMER_H

#include <chrono>

using namespace std::chrono;

template <class unit = nanoseconds>
class Timer {
  using clock = high_resolution_clock;

public:
  Timer() : fStart(), fStop() { Start(); }

  void Reset() { Start(); }

  void Start() { fStart = clock::now(); }

  double Elapsed()
  {
    fStop = clock::now();
    return duration_cast<unit>(fStop - fStart).count();
  }

private:
  high_resolution_clock::time_point fStart, fStop;
};

#if !defined(VECCORE_CUDA_DEVICE_COMPILATION)

class cycles {
};

template <>
class Timer<cycles> {
public:
  Timer() { Start(); }

  void Reset() { Start(); }

  void Start() { fStart = GetCycleCount(); }

  double Elapsed() { return static_cast<double>(GetCycleCount() - fStart); }

private:
  unsigned long long int fStart;

  inline __attribute__((always_inline)) unsigned long long int GetCycleCount()
  {
    unsigned int hi, lo;
    asm volatile("cpuid\n\t"
                 "rdtsc"
                 : "=a"(lo), "=d"(hi));
    return ((unsigned long long)lo) | (((unsigned long long)hi) << 32);
  }
};
#endif

#endif
