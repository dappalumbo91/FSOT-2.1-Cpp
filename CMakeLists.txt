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
if(MSVC)
  # Formulas use UCNs. Without /utf-8 the ones that fit in code page 1252 become single
  # bytes (U+00B7 -> 0xB7); nlohmann::json::dump throws type_error.316 and fsot_freeze_domain
  # exits 0xC0000409. Names such as BP_H₂O are replaced with '?' and fail the goldens.
  add_compile_options(/utf-8)
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

# Freestanding core (seeds, layers, nest, S law) vs the host engine: bit-identical in balanced ternary.
add_executable(test_core tests/test_core.cpp)
target_link_libraries(test_core PRIVATE fsot)
add_test(NAME core_vs_engine COMMAND test_core)
add_executable(test_core_closed_forms tests/test_core_closed_forms.cpp)
target_include_directories(test_core_closed_forms PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_compile_definitions(test_core_closed_forms PRIVATE FSOT_GOLDEN_TSV="${CMAKE_CURRENT_SOURCE_DIR}/golden/golden_AEB2AD.tsv")
add_test(NAME core_closed_forms_vs_golden COMMAND test_core_closed_forms)
add_executable(predict_closed_form apps/predict_closed_form.cpp)
target_include_directories(predict_closed_form PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include)
add_test(NAME predict_closed_form_smoke COMMAND predict_closed_form --name H0 --digits 12)

# Ledger A emit + property routing (generated tables; needs a >=113-bit type for float(value) exactness).
if(Boost_FOUND OR FSOT_WITH_FLOAT128)
  add_executable(test_ledger_a_routing tests/test_ledger_a_routing.cpp)
  target_link_libraries(test_ledger_a_routing PRIVATE fsot)
  target_compile_definitions(test_ledger_a_routing PRIVATE FSOT_LA_GOLDEN="${CMAKE_CURRENT_SOURCE_DIR}/golden/ledger_a_routing.tsv")
  add_test(NAME ledger_a_routing COMMAND test_ledger_a_routing)
  add_executable(fsot_look_elsewhere apps/fsot_look_elsewhere.cpp)
  target_link_libraries(fsot_look_elsewhere PRIVATE fsot)
  add_test(NAME look_elsewhere_smoke COMMAND fsot_look_elsewhere)
endif()

# Hub seed leaves (scripts/*_seed_check.py @ ledger_b_data_commit) and the z <= 1 precision gate.
if(Boost_FOUND)
  add_executable(test_seed_leaves tests/test_seed_leaves.cpp)
  target_link_libraries(test_seed_leaves PRIVATE fsot)
  target_compile_definitions(test_seed_leaves PRIVATE FSOT_SEED_LEAVES_TSV="${CMAKE_CURRENT_SOURCE_DIR}/golden/seed_leaves_6f9c2560.tsv")
  add_test(NAME seed_leaves COMMAND test_seed_leaves)
  add_executable(fsot_precision apps/fsot_precision.cpp)
  target_link_libraries(fsot_precision PRIVATE fsot)
  add_test(NAME precision_report
           COMMAND fsot_precision --refs ${CMAKE_CURRENT_SOURCE_DIR}/reference/published_2026-10-02.tsv
                   --map ${CMAKE_CURRENT_SOURCE_DIR}/reference/prediction_map_2026-10-02.tsv
                   --lineage ${CMAKE_CURRENT_SOURCE_DIR}/reference/pin_lineage_2026-10-02.tsv
                   --tsv-out ${CMAKE_CURRENT_BINARY_DIR}/precision_2026-10-02.tsv
                   --md-out ${CMAKE_CURRENT_BINARY_DIR}/precision_2026-10-02.md)
  add_test(NAME precision_report_tsv COMMAND ${CMAKE_COMMAND} -E compare_files
           ${CMAKE_CURRENT_BINARY_DIR}/precision_2026-10-02.tsv ${CMAKE_CURRENT_SOURCE_DIR}/audit/precision_2026-10-02.tsv)
  set_tests_properties(precision_report_tsv PROPERTIES DEPENDS precision_report)
  add_test(NAME precision_report_md COMMAND ${CMAKE_COMMAND} -E compare_files
           ${CMAKE_CURRENT_BINARY_DIR}/precision_2026-10-02.md ${CMAKE_CURRENT_SOURCE_DIR}/audit/precision_2026-10-02.md)
  set_tests_properties(precision_report_md PROPERTIES DEPENDS precision_report)
endif()
if(Python3_Interpreter_FOUND)
  add_test(NAME references_check COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/check_references.py)
  add_test(NAME refinement_freeze COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_refinement_freeze.py)
  add_test(NAME refinement_freeze_b COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_refinement_freeze_b.py)
  add_test(NAME refinements_b_crosscheck COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/crosscheck_refinements_b.py)
  add_test(NAME refinement_freeze_c COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_c.py)
  add_test(NAME refinement_freeze_d COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_d.py)
  add_test(NAME derivations_freeze_e COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_e.py)
  add_test(NAME derivations_freeze_f COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_f.py)
  add_test(NAME derivations_freeze_g COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_g.py)
  add_test(NAME round_freeze_h COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_h.py)
  add_test(NAME round_freeze_i COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_i.py)
  add_test(NAME round_freeze_j COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_j.py)
  add_test(NAME round_freeze_k COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_k.py)
  add_test(NAME round_freeze_l COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_l.py)
  add_test(NAME round_freeze_m COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_m.py)
  add_test(NAME round_freeze_n COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_n.py)
  add_test(NAME round_freeze_o COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_o.py)
  add_test(NAME round_freeze_p COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_p.py)
  add_test(NAME round_freeze_q COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_q.py)
  add_test(NAME round_freeze_r COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_r.py)
  add_test(NAME round_freeze_s COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_s.py)
  add_test(NAME round_freeze_s2 COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_s2.py)
  add_test(NAME round_freeze_t COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_t.py)
  add_test(NAME round_freeze_u COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_u.py)
  add_test(NAME round_freeze_u2 COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_u2.py)
  add_test(NAME round_freeze_v COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_v.py)
  add_test(NAME round_freeze_w COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_w.py)
  add_test(NAME round_freeze_x COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_x.py)
  add_test(NAME round_freeze_y COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_y.py)
  add_test(NAME round_freeze_z COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_z.py)
  add_test(NAME round_freeze_aa COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_aa.py)
  add_test(NAME round_freeze_ab COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_ab.py)
  add_test(NAME round_freeze_ac COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_ac.py)
  add_test(NAME round_freeze_ad COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_ad.py)
  add_test(NAME round_freeze_ae COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_ae.py)
  add_test(NAME round_freeze_af COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_af.py)
  add_test(NAME round_freeze_ag COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_ag.py)
  add_test(NAME round_freeze_ah COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_ah.py)
  add_test(NAME round_freeze_ai COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_ai.py)
  add_test(NAME round_freeze_aj COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_aj.py)
  add_test(NAME round_freeze_ak COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_ak.py)
  add_test(NAME round_freeze_al COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_al.py)
  add_test(NAME round_freeze_am COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_am.py)
  add_test(NAME round_freeze_an COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_an.py)
  add_test(NAME round_freeze_ao COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_ao.py)
  add_test(NAME round_freeze_ap COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_ap.py)
  add_test(NAME round_freeze_aq COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_aq.py)
  add_test(NAME round_freeze_ar COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_ar.py)
  add_test(NAME round_freeze_as COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_as.py)
  add_test(NAME round_freeze_at COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_at.py)
  add_test(NAME round_freeze_au COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_au.py)
  add_test(NAME round_freeze_av COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_av.py)
  add_test(NAME round_freeze_aw COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_aw.py)
  add_test(NAME round_freeze_ax COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_ax.py)
  add_test(NAME round_freeze_ay COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_ay.py)
  add_test(NAME round_freeze_az COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze_files_az.py)
endif()

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
  # dated SHA-256 freeze writer/verifier (docs/FREEZES.md)
  add_executable(fsot_freeze_domain apps/fsot_freeze_domain.cpp)
  target_link_libraries(fsot_freeze_domain PRIVATE fsot nlohmann_json::nlohmann_json)
  add_test(NAME freeze_core_sha_matches_hub_freeze
           COMMAND ${CMAKE_COMMAND} -DEXE=$<TARGET_FILE:fsot_freeze_domain> -DEXPECT=8e30e85e72091462c4d66df2d498afb36ccbc2d40eb5df01b4e083947c79dad3
                   -P ${CMAKE_CURRENT_SOURCE_DIR}/cmake/check_core_sha.cmake)   # portable: no sh (native Windows CTest)
  find_package(Python3 COMPONENTS Interpreter QUIET)
  file(GLOB FSOT_FREEZES ${CMAKE_CURRENT_SOURCE_DIR}/freezes/*.json)
  foreach(fz ${FSOT_FREEZES})
    get_filename_component(fzn ${fz} NAME_WE)
    add_test(NAME freeze_verify_${fzn} COMMAND fsot_freeze_domain --verify ${fz})
    if(Python3_Interpreter_FOUND)
      add_test(NAME freeze_verify_py_${fzn} COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_freeze.py ${fz})
    endif()
  endforeach()
  if(FSOT_HUB_DATA)
    add_test(NAME ledger_b COMMAND fsot_ledger_b --hub ${FSOT_HUB_DATA} --golden ${CMAKE_CURRENT_SOURCE_DIR}/golden/ledger_b_6f9c2560.tsv
             --corrected-out ${CMAKE_CURRENT_BINARY_DIR}/ledger_b_corrected.tsv
             --genuine-misses-out ${CMAKE_CURRENT_BINARY_DIR}/ledger_b_genuine_misses.tsv
             --tier-evidence ${CMAKE_CURRENT_SOURCE_DIR}/golden/tier_evidence_6f9c2560.json
             --tiers-out ${CMAKE_CURRENT_BINARY_DIR}/evidence_tiers.tsv)
    add_test(NAME evidence_tiers_report COMMAND ${CMAKE_COMMAND} -E compare_files
             ${CMAKE_CURRENT_BINARY_DIR}/evidence_tiers.tsv ${CMAKE_CURRENT_SOURCE_DIR}/golden/evidence_tiers_6f9c2560.tsv)
    set_tests_properties(evidence_tiers_report PROPERTIES DEPENDS ledger_b)
    add_test(NAME ledger_b_corrected_report COMMAND ${CMAKE_COMMAND} -E compare_files
             ${CMAKE_CURRENT_BINARY_DIR}/ledger_b_corrected.tsv ${CMAKE_CURRENT_SOURCE_DIR}/golden/ledger_b_corrected_6f9c2560.tsv)
    set_tests_properties(ledger_b_corrected_report PROPERTIES DEPENDS ledger_b)
    add_test(NAME ledger_b_genuine_misses COMMAND ${CMAKE_COMMAND} -E compare_files
             ${CMAKE_CURRENT_BINARY_DIR}/ledger_b_genuine_misses.tsv ${CMAKE_CURRENT_SOURCE_DIR}/golden/ledger_b_genuine_misses_6f9c2560.tsv)
    set_tests_properties(ledger_b_genuine_misses PROPERTIES DEPENDS ledger_b)
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
