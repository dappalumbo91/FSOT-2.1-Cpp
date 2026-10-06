#!/usr/bin/env python3
"""D-wave lbar_1 and lbar_2 under FREEZE_2026-10-02bh. Prints the score. Does not edit the gate."""
from mpmath import mp, mpf, pi, sqrt, log, fabs

mp.dps = 50
mp_MeV = mpf("938.27208927034090404")
M = mpf("139.57034107031817487")
Nc = mpf(3)
F = (mp_MeV / 3) * sqrt(Nc) / (2 * pi)
m2 = 8 * pi ** 2 * F ** 2
m = sqrt(m2)
phase = 1 - 4 * M ** 2 / m2
Gamma = (pi * m / 12) * phase ** (mpf("1.5"))
a20 = (mpf(24) / 5) * Gamma * (m2 + 4 * M ** 2) / (m ** 4 * (m2 - 4 * M ** 2) ** (mpf("1.5")))
b11 = 16 * Gamma / (m ** 4 * sqrt(m2 - 4 * M ** 2))
A = 1440 * pi ** 3 * F ** 4 * a20
B = 288 * pi ** 3 * F ** 4 * b11
sum4 = A + mpf(53) / 8
diff = B - mpf(97) / 120
l2 = (sum4 + diff) / 5
l1 = l2 - diff
z1 = fabs(l1 - mpf("-0.4")) / mpf("0.6")
z2 = fabs(l2 - mpf("4.3")) / mpf("0.1")
print(f"lbar_1 {l1}")
print(f"lbar_2 {l2}")
print(f"z1 {z1}")
print(f"z2 {z2}")
print(f"m {m}")
print(f"Gamma {Gamma}")
