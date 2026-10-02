cmake_minimum_required(VERSION 3.20)
if(POLICY CMP0167)
  cmake_policy(SET CMP0167 NEW)
endif()
project(fsot_cpp VERSION 0.1.0 LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

option(FSOT_WITH_BOOST_MP "Use Boost.Multiprecision cpp_bin_float<169> (header-only, matches mpmath dps=50)" ON)
option(FSOT_WITH_FLOAT128 "Use GCC __float128 / libquadmath where available" ON)
set(FSOT_AUTHORITY "" CACHE FILEPATH "Path to FSOT-2.1-Lean vendor/fsot_compute.py (enables regen + golden refresh)")
find_package(Python3 COMPONENTS Interpreter)

add_library(fsot INTERFACE)
target_include_directories(fsot INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_compile_features(fsot INTERFACE cxx_std_20)
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
  # No FMA contraction: double results must be bit-identical to CPython's float arithmetic.
  target_compile_options(fsot INTERFACE -ffp-contract=off)
endif()

if(FSOT_WITH_BOOST_MP)
  find_package(Boost 1.75 CONFIG QUIET)
  if(Boost_FOUND)
    target_link_libraries(fsot INTERFACE Boost::headers)
    target_compile_definitions(fsot INTERFACE FSOT_HAVE_BOOST_MP)
    message(STATUS "fsot: Boost.Multiprecision ${Boost_VERSION} (mp169)")
  else()
    message(WARNING "fsot: Boost not found; 50-digit type disabled")
  endif()
endif()

if(FSOT_WITH_FLOAT128 AND CMAKE_CXX_COMPILER_ID MATCHES "GNU" AND CMAKE_SYSTEM_PROCESSOR MATCHES "x86_64|AMD64")
  target_compile_definitions(fsot INTERFACE FSOT_HAVE_FLOAT128)
  target_link_libraries(fsot INTERFACE quadmath)
  message(STATUS "fsot: __float128 enabled")
endif()

# Optional: regenerate the closed-form sections and golden file from the authority (pin-verified).
if(FSOT_AUTHORITY AND Python3_FOUND)
  add_custom_target(fsot_regen
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/gen_closed_forms.py --authority ${FSOT_AUTHORITY}
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/dump_golden.py --authority ${FSOT_AUTHORITY}
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    COMMENT "Regenerating closed forms + golden values from pinned authority")
endif()

add_executable(fsot_report apps/fsot_report.cpp)
target_link_libraries(fsot_report PRIVATE fsot)

enable_testing()
add_executable(test_golden tests/test_golden.cpp)
target_link_libraries(test_golden PRIVATE fsot)
target_compile_definitions(test_golden PRIVATE FSOT_GOLDEN_TSV="${CMAKE_CURRENT_SOURCE_DIR}/golden/golden_AEB2AD.tsv")
add_test(NAME golden COMMAND test_golden)

add_executable(test_trit tests/test_trit.cpp)
target_link_libraries(test_trit PRIVATE fsot)
add_test(NAME trit COMMAND test_trit)

add_executable(test_ternary tests/test_ternary.cpp)
target_link_libraries(test_ternary PRIVATE fsot)
target_compile_definitions(test_ternary PRIVATE FSOT_GOLDEN_TSV="${CMAKE_CURRENT_SOURCE_DIR}/golden/golden_AEB2AD.tsv")
add_test(NAME ternary COMMAND test_ternary)

# Freestanding check: the balanced-ternary core compiles without a hosted library and references no
# heap / exception / stdio / libm symbols.
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
  add_library(fsot_freestanding_check OBJECT tests/freestanding_check.cpp)
  target_include_directories(fsot_freestanding_check PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include)
  target_compile_options(fsot_freestanding_check PRIVATE -ffreestanding -fno-exceptions -fno-rtti -fno-threadsafe-statics -O2)
  find_program(FSOT_NM NAMES nm)
  if(FSOT_NM)
    add_test(NAME freestanding_symbols
      COMMAND sh -c "! ${FSOT_NM} -u -C $<TARGET_OBJECTS:fsot_freestanding_check> | grep -E 'malloc|free|operator new|operator delete|__cxa_throw|__cxa_guard|printf|puts|std::|\\b(exp|log|sin|cos|sqrt|pow)\\b'")
  endif()
endif()

# Ledger B / benchmark margin audit re-scorer (host tool; needs nlohmann_json and a >=113-bit type).
find_package(nlohmann_json 3.2 QUIET)
set(FSOT_HUB_DATA "" CACHE PATH "FSOT-2.1-Lean checkout at AUTHORITY_PIN.json ledger_b_data_commit (enables the ledger_b test)")
if(nlohmann_json_FOUND AND (Boost_FOUND OR FSOT_WITH_FLOAT128))
  add_executable(fsot_ledger_b apps/fsot_ledger_b.cpp)
  target_link_libraries(fsot_ledger_b PRIVATE fsot nlohmann_json::nlohmann_json)
  if(FSOT_HUB_DATA)
    add_test(NAME ledger_b COMMAND fsot_ledger_b --hub ${FSOT_HUB_DATA} --golden ${CMAKE_CURRENT_SOURCE_DIR}/golden/ledger_b_6f9c2560.tsv)
  endif()
else()
  message(STATUS "fsot: nlohmann_json not found; fsot_ledger_b disabled")
endif()

add_executable(bench_ternary bench/bench_ternary.cpp)
target_link_libraries(bench_ternary PRIVATE fsot)
target_compile_definitions(bench_ternary PRIVATE FSOT_GOLDEN_TSV="${CMAKE_CURRENT_SOURCE_DIR}/golden/golden_AEB2AD.tsv")
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
  target_compile_options(bench_ternary PRIVATE -O3 -march=native)
endif()

add_executable(bench_cpp bench/bench_cpp.cpp)
target_link_libraries(bench_cpp PRIVATE fsot)
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
  target_compile_options(bench_cpp PRIVATE -O3 -march=native)
endif()
