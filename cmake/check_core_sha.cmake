# Portable core-SHA check for CTest (no sh needed; works with native Windows CTest).
# Usage: cmake -DEXE=<fsot_freeze_domain> -DEXPECT=<sha256> -P check_core_sha.cmake
execute_process(COMMAND "${EXE}" --print-core-sha OUTPUT_VARIABLE out RESULT_VARIABLE rc OUTPUT_STRIP_TRAILING_WHITESPACE)
if(NOT rc EQUAL 0)
  message(FATAL_ERROR "fsot_freeze_domain --print-core-sha failed (exit ${rc})")
endif()
string(STRIP "${out}" out)
if(NOT out STREQUAL "${EXPECT}")
  message(FATAL_ERROR "core sha mismatch: got '${out}', expected '${EXPECT}'")
endif()
message(STATUS "core sha matches hub freeze: ${out}")
