// fsot/host/pyjson.hpp — Python-semantics helpers over nlohmann::json (host tools only).
// Reproduces the exact behaviour of the Python expressions used by the hub scripts:
// json.loads (incl. NaN/Infinity), truthiness, str(), float(), int(), round(x, n), repr(float),
// statistics.median.
#pragma once
#include <algorithm>
#include <cctype>
#include <charconv>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <optional>
#include <string>
#include <string_view>
#include <vector>

#include <nlohmann/json.hpp>

namespace fsot::py {
using json = nlohmann::json;

// json.loads(text): Python's json module also accepts the non-standard tokens NaN, Infinity, -Infinity.
// They are rewritten to sentinel strings outside string literals, parsed, and restored as doubles.
inline void restore_nonfinite(json& j) {
  if (j.is_string()) {
    const auto& s = j.get_ref<const std::string&>();
    if (s == "\x01PY_NaN") j = std::nan("");
    else if (s == "\x01PY_Inf") j = HUGE_VAL;
    else if (s == "\x01PY_-Inf") j = -HUGE_VAL;
  } else if (j.is_structured()) {
    for (auto& v : j) restore_nonfinite(v);
  }
}
inline std::optional<json> loads(const std::string& text) {
  std::string t;
  bool in_str = false, esc = false, any = false;
  t.reserve(text.size());
  for (std::size_t i = 0; i < text.size(); ++i) {
    const char c = text[i];
    if (in_str) {
      t += c;
      if (esc) esc = false;
      else if (c == '\\') esc = true;
      else if (c == '"') in_str = false;
      continue;
    }
    if (c == '"') { in_str = true; t += c; continue; }
    if (text.compare(i, 3, "NaN") == 0) { t += "\"\\u0001PY_NaN\""; i += 2; any = true; continue; }
    if (text.compare(i, 8, "Infinity") == 0) { t += "\"\\u0001PY_Inf\""; i += 7; any = true; continue; }
    if (text.compare(i, 9, "-Infinity") == 0) { t += "\"\\u0001PY_-Inf\""; i += 8; any = true; continue; }
    t += c;
  }
  json j = json::parse(t, nullptr, /*allow_exceptions=*/false);
  if (j.is_discarded()) return std::nullopt;
  if (any) restore_nonfinite(j);
  return j;
}

inline bool truthy(const json& v) {
  switch (v.type()) {
    case json::value_t::null: return false;
    case json::value_t::boolean: return v.get<bool>();
    case json::value_t::number_integer: return v.get<std::int64_t>() != 0;
    case json::value_t::number_unsigned: return v.get<std::uint64_t>() != 0;
    case json::value_t::number_float: return v.get<double>() != 0.0;
    case json::value_t::string: return !v.get_ref<const std::string&>().empty();
    case json::value_t::array: case json::value_t::object: return !v.empty();
    default: return false;
  }
}

// repr(float) — CPython 'r' format: shortest round-trip digits; fixed if -4 <= exp < 16.
inline std::string repr(double x) {
  if (std::isnan(x)) return "nan";
  if (std::isinf(x)) return x > 0 ? "inf" : "-inf";
  if (x == 0) return std::signbit(x) ? "-0.0" : "0.0";
  char buf[64];
  auto res = std::to_chars(buf, buf + sizeof buf, x, std::chars_format::scientific);
  std::string s(buf, res.ptr);
  bool neg = s[0] == '-';
  if (neg) s.erase(0, 1);
  const auto epos = s.find('e');
  std::string mant = s.substr(0, epos);
  int exp10 = std::atoi(s.c_str() + epos + 1);
  std::string digits;
  for (char c : mant) if (c != '.') digits += c;
  std::string out;
  if (exp10 >= -4 && exp10 < 16) {
    const int nd = static_cast<int>(digits.size());
    if (exp10 >= 0) {
      if (nd <= exp10 + 1) out = digits + std::string(exp10 + 1 - nd, '0') + ".0";
      else out = digits.substr(0, exp10 + 1) + "." + digits.substr(exp10 + 1);
    } else {
      out = "0." + std::string(-exp10 - 1, '0') + digits;
    }
  } else {
    out = digits.substr(0, 1);
    if (digits.size() > 1) out += "." + digits.substr(1);
    char eb[16];
    std::snprintf(eb, sizeof eb, "e%c%02d", exp10 < 0 ? '-' : '+', std::abs(exp10));
    out += eb;
  }
  return neg ? "-" + out : out;
}

// str(value) for a json-loaded scalar (containers are not reached by the gates).
inline std::string str(const json& v) {
  switch (v.type()) {
    case json::value_t::null: return "None";
    case json::value_t::boolean: return v.get<bool>() ? "True" : "False";
    case json::value_t::number_integer: return std::to_string(v.get<std::int64_t>());
    case json::value_t::number_unsigned: return std::to_string(v.get<std::uint64_t>());
    case json::value_t::number_float: return repr(v.get<double>());
    case json::value_t::string: return v.get<std::string>();
    default: return "<container>";
  }
}
// str(x.get(key) or "")
inline std::string str_or_empty(const json& obj, const char* key) {
  auto it = obj.find(key);
  if (it == obj.end() || !truthy(*it)) return "";
  return str(*it);
}
inline const json* get(const json& obj, const char* key) {
  auto it = obj.find(key);
  return it == obj.end() ? nullptr : &*it;
}
inline bool is_none(const json* v) { return v == nullptr || v->is_null(); }

inline std::string lower_ascii(std::string s) {
  for (auto& c : s) if (c >= 'A' && c <= 'Z') c = char(c - 'A' + 'a');
  return s;
}
inline bool ends_with(std::string_view s, std::string_view suf) { return s.size() >= suf.size() && s.substr(s.size() - suf.size()) == suf; }
inline bool starts_with(std::string_view s, std::string_view pre) { return s.substr(0, pre.size()) == pre; }
inline bool contains(std::string_view s, std::string_view t) { return s.find(t) != std::string_view::npos; }

// float(str): surrounding whitespace, inf/nan words, underscores between digits.
inline std::optional<double> float_from_string(std::string s) {
  auto ws = [](char c) { return c == ' ' || c == '\t' || c == '\n' || c == '\r' || c == '\f' || c == '\v'; };
  while (!s.empty() && ws(s.front())) s.erase(0, 1);
  while (!s.empty() && ws(s.back())) s.pop_back();
  if (s.empty()) return std::nullopt;
  std::string t;
  for (std::size_t i = 0; i < s.size(); ++i) {
    if (s[i] == '_') {
      if (i == 0 || i + 1 == s.size() || !std::isdigit((unsigned char)s[i - 1]) || !std::isdigit((unsigned char)s[i + 1])) return std::nullopt;
      continue;
    }
    t += s[i];
  }
  std::string l = lower_ascii(t);
  std::string body = (l[0] == '+' || l[0] == '-') ? l.substr(1) : l;
  const double sign = l[0] == '-' ? -1.0 : 1.0;
  if (body == "inf" || body == "infinity") return sign * HUGE_VAL;
  if (body == "nan") return std::nan("");
  for (char c : body) if (!(std::isdigit((unsigned char)c) || c == '.' || c == 'e' || c == '+' || c == '-')) return std::nullopt;
  char* end = nullptr;
  double v = std::strtod(t.c_str(), &end);
  if (end != t.c_str() + t.size()) return std::nullopt;
  return v;
}
// float(value): nullopt where Python raises TypeError/ValueError.
inline std::optional<double> to_float(const json& v) {
  switch (v.type()) {
    case json::value_t::boolean: return v.get<bool>() ? 1.0 : 0.0;
    case json::value_t::number_integer: return static_cast<double>(v.get<std::int64_t>());
    case json::value_t::number_unsigned: return static_cast<double>(v.get<std::uint64_t>());
    case json::value_t::number_float: return v.get<double>();
    case json::value_t::string: return float_from_string(v.get<std::string>());
    default: return std::nullopt;
  }
}
// int(value) (int() of a float truncates; of a str must be integral).
inline std::optional<long long> to_int(const json& v) {
  switch (v.type()) {
    case json::value_t::boolean: return v.get<bool>() ? 1 : 0;
    case json::value_t::number_integer: return v.get<std::int64_t>();
    case json::value_t::number_unsigned: return static_cast<long long>(v.get<std::uint64_t>());
    case json::value_t::number_float: { double d = v.get<double>(); if (!std::isfinite(d)) return std::nullopt; return static_cast<long long>(std::trunc(d)); }
    case json::value_t::string: {
      std::string s = v.get<std::string>();
      while (!s.empty() && std::isspace((unsigned char)s.front())) s.erase(0, 1);
      while (!s.empty() && std::isspace((unsigned char)s.back())) s.pop_back();
      long long out = 0;
      auto r = std::from_chars(s.data() + (s.size() && s[0] == '+'), s.data() + s.size(), out);
      if (r.ec != std::errc() || r.ptr != s.data() + s.size()) return std::nullopt;
      return out;
    }
    default: return std::nullopt;
  }
}
// value == 0 in Python (None handled by caller); False == 0 is True.
inline bool eq_zero(const json& v) {
  if (v.is_boolean()) return !v.get<bool>();
  if (v.is_number()) return v.get<double>() == 0.0;
  return false;
}

// round(x, nd) for floats: exact decimal rounding (half-even on the exact binary value), back to double.
inline double round_nd(double x, int nd) {
  if (!std::isfinite(x)) return x;
  char buf[512];
  std::snprintf(buf, sizeof buf, "%.*f", nd, x);
  return std::strtod(buf, nullptr);
}

inline std::optional<double> median(std::vector<double> v) {
  if (v.empty()) return std::nullopt;
  std::sort(v.begin(), v.end());
  const std::size_t n = v.size();
  if (n % 2) return v[n / 2];
  return (v[n / 2 - 1] + v[n / 2]) / 2.0;
}

}  // namespace fsot::py
