/* NATIVEX2: the second wave of whole-stage kernels, one library (scripts/build_nx2_native.sh).
 * Each lever lives in its own nx2_<lever>.c; this file only carries the version symbol.
 * Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
 * Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md. */
#include <stdint.h>

int64_t nx2_version(void) { return 1; }
