/* Copyright (C) 2021 Hiroo HAYASHI

   This file is part of Embench and was formerly part of the Bristol/Embecosm
   Embedded Benchmark Suite.

   SPDX-License-Identifier: GPL-3.0-or-later */

#include <support.h>
#include <stdint.h>
#include <inttypes.h>
#include <stdio.h>

static uint64_t cycle;

#if __riscv_xlen == 64
uint64_t
rdcycle ()
{
  uint64_t cycle;
  // cf. RISC-V Unprivileged ISA, 10.1 Base Counters and Timers
  __asm__ __volatile__ ("csrr %0, cycle\n" : "=r" (cycle));
  return (uint64_t) cycle;
}
#else
uint64_t
rdcycle ()
{
  uint32_t lo, hi1, hi2;
  // cf. RISC-V Unprivileged ISA, 10.1 Base Counters and Timers
  __asm__ __volatile__ ("1:\n\t"                     \
                        "csrr %1, cycle\n\t"        \
                        "csrr %0, cycleh\n\t"       \
                        "csrr %2, cycleh\n\t"       \
                        "bne  %0, %2, 1b\n\t"        \
                        : "=r" (hi1), "=r" (lo), "=r" (hi2));
  return (uint64_t)hi1 << 32 | lo;
}
#endif

void __attribute__ ((noinline)) __attribute__ ((externally_visible))
initialise_board ()
{
  __asm__ volatile ("li a0, 0" : : : "memory");
}

void __attribute__ ((noinline)) __attribute__ ((externally_visible))
start_trigger ()
{
  cycle = rdcycle();
}

void __attribute__ ((noinline)) __attribute__ ((externally_visible))
stop_trigger ()
{
  cycle = rdcycle() - cycle;
  // https://stackoverflow.com/questions/9225567/how-to-portably-print-a-int64-t-type-in-c
  printf("cycle = 0x%016" PRIx64 "\n", cycle);
}