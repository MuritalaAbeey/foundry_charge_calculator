#!/usr/bin/env python3
"""
Foundry Lab Alloy Charge Calculator
-----------------------------------
Follows the procedure in "Charge Calculation for Al-Si-Cu-Mg-Graphite Composites":

  1. Enter each sample composition (wt%).
  2. Alloy density       = sum( wt%/100 * element density )
  3. Single pattern mass = alloy density * pattern volume
  4. Element mass        = (wt%/100 * single pattern mass) * samples per composition
                           * allowance factor
     where allowance factor = 1 + allowance%/100  (100 % allowance -> x2)
  5. Total mass of each constituent = sum over all compositions.

Inputs requested before calculation starts:
  number of elements, element names, element densities, total (pattern) volume,
  number of samples (compositions), percentage allowance, samples per composition.
"""


# ----------------------------------------------------------------------------
# Input helpers
# ----------------------------------------------------------------------------
def ask_int(prompt, minimum=1):
    while True:
        try:
            value = int(input(prompt).strip())
            if value >= minimum:
                return value
            print(f"  Please enter a whole number >= {minimum}.")
        except ValueError:
            print("  Invalid input. Please enter a whole number.")


def ask_float(prompt, minimum=0.0, strictly_greater=False):
    while True:
        try:
            value = float(input(prompt).strip())
            if (value > minimum) if strictly_greater else (value >= minimum):
                return value
            cmp = ">" if strictly_greater else ">="
            print(f"  Please enter a number {cmp} {minimum}.")
        except ValueError:
            print("  Invalid input. Please enter a number.")


def ask_name(prompt, existing):
    while True:
        name = input(prompt).strip()
        if not name:
            print("  Name cannot be empty.")
        elif name.lower() in (n.lower() for n in existing):
            print("  That element name is already used.")
        else:
            return name


# ----------------------------------------------------------------------------
# Data collection
# ----------------------------------------------------------------------------
def collect_inputs():
    print("=" * 70)
    print("        FOUNDRY LAB ALLOY CHARGE CALCULATOR")
    print("=" * 70)

    n_elem = ask_int("Number of elements in the alloy/composite: ", 1)

    names, densities = [], []
    for i in range(1, n_elem + 1):
        name = ask_name(f"  Name of element {i} (e.g. Al, Graphite): ", names)
        dens = ask_float(f"  Density of {name} (g/cm3): ", 0.0, strictly_greater=True)
        names.append(name)
        densities.append(dens)

    volume = ask_float("\nTotal volume of one pattern (cm3): ", 0.0, strictly_greater=True)
    n_samples = ask_int("Number of samples (compositions): ", 1)
    allowance = ask_float("Percentage allowance (%), e.g. 100 for x2: ", 0.0)
    per_comp = ask_int("Number of sample(s) per composition: ", 1)

    return names, densities, volume, n_samples, allowance, per_comp


def collect_compositions(names, n_samples):
    """Ask for wt% of every element in every sample; each sample must total 100 %."""
    print("\nEnter the composition (wt%) of each sample. Each must total 100 %.")
    samples = []
    for s in range(n_samples):
        label = input(f"\nName of sample {s + 1} [default: Sample {s + 1}]: ").strip() \
            or f"Sample {s + 1}"
        while True:
            wts = [ask_float(f"  {label} - {n} (wt%): ", 0.0) for n in names]
            total = sum(wts)
            if abs(total - 100.0) <= 0.01:
                break
            print(f"  Total is {total:.3f} wt% (must be 100). Re-enter this sample.")
        samples.append((label, wts))
    return samples


# ----------------------------------------------------------------------------
# Calculation
# ----------------------------------------------------------------------------
def calculate(names, densities, volume, samples, allowance, per_comp):
    allowance_factor = 1.0 + allowance / 100.0
    multiplier = per_comp * allowance_factor

    results = []
    totals = [0.0] * len(names)

    for label, wts in samples:
        density = sum((w / 100.0) * d for w, d in zip(wts, densities))
        # Rounded to 2 d.p. so results reproduce the worked document exactly
        pattern_mass = round(density * volume, 2)
        masses = [(w / 100.0) * pattern_mass * multiplier for w in wts]
        totals = [t + m for t, m in zip(totals, masses)]
        results.append((label, wts, density, pattern_mass, masses))

    return results, totals, allowance_factor, multiplier


# ----------------------------------------------------------------------------
# Reporting
# ----------------------------------------------------------------------------
def report(names, densities, volume, results, totals, allowance,
           allowance_factor, multiplier, per_comp):
    print("\n" + "=" * 70)
    print("                 CHARGE CALCULATION RESULTS")
    print("=" * 70)
    print(f"Pattern volume          : {volume:.3f} cm3")
    print(f"Samples per composition : {per_comp}")
    print(f"Allowance               : {allowance:g} %  (factor = {allowance_factor:g})")
    print(f"Batch multiplier        : {per_comp} x {allowance_factor:g} = {multiplier:g}")

    print("\nElement densities:")
    for n, d in zip(names, densities):
        print(f"  {n:<15} {d:.3f} g/cm3")

    print("\n" + "-" * 70)
    print("MASS OF ALLOY SAMPLES & INDIVIDUAL CONSTITUENTS")
    print("-" * 70)
    for label, wts, density, pattern_mass, masses in results:
        comp = ", ".join(f"{w:g}% {n}" for w, n in zip(wts, names))
        print(f"\n{label}: {comp}")
        terms = " + ".join(f"({w:g}/100 * {d:g})" for w, d in zip(wts, densities))
        print(f"  Density             = {terms} = {density:.4f} g/cm3")
        print(f"  Single pattern mass = {density:.4f} * {volume:g} = {pattern_mass:.2f} g")
        for n, w, m in zip(names, wts, masses):
            print(f"  Mass of {w:g}% {n:<10}: ({w:g}/100 * {pattern_mass:.2f}) "
                  f"* {per_comp} * {allowance_factor:g} = {m:.2f} g")

    print("\n" + "-" * 70)
    print("TOTAL MASS REQUIRED FOR EACH CONSTITUENT")
    print("-" * 70)
    for i, n in enumerate(names):
        parts = " + ".join(f"{r[4][i]:.2f}" for r in results)
        print(f"\nTotal {n}: {parts}")
        print(f"        = {totals[i]:.2f} g = {totals[i] / 1000:.3f} kg")

    print("\n" + "-" * 70)
    print("SUMMARY TABLE OF RAW MATERIAL REQUIREMENTS")
    print("-" * 70)
    print(f"{'Constituent':<18}{'Total mass (g)':>18}{'Total mass (kg)':>18}")
    for n, t in zip(names, totals):
        print(f"{n:<18}{t:>18.2f}{t / 1000:>18.3f}")
    print(f"{'TOTAL CHARGE':<18}{sum(totals):>18.2f}{sum(totals) / 1000:>18.3f}")
    print("=" * 70)


def save_csv(names, results, totals, path):
    import csv
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Sample", "Density (g/cm3)", "Pattern mass (g)"]
                   + [f"{n} (g)" for n in names])
        for label, wts, density, pm, masses in results:
            w.writerow([label, f"{density:.4f}", f"{pm:.2f}"]
                       + [f"{m:.2f}" for m in masses])
        w.writerow(["TOTAL", "", ""] + [f"{t:.2f}" for t in totals])


# ----------------------------------------------------------------------------
def main():
    names, densities, volume, n_samples, allowance, per_comp = collect_inputs()
    samples = collect_compositions(names, n_samples)

    results, totals, allowance_factor, multiplier = calculate(
        names, densities, volume, samples, allowance, per_comp)

    report(names, densities, volume, results, totals, allowance,
           allowance_factor, multiplier, per_comp)

    if input("\nSave results to CSV? (y/n): ").strip().lower() == "y":
        path = input("File name [charge_results.csv]: ").strip() or "charge_results.csv"
        save_csv(names, results, totals, path)
        print(f"Saved to {path}")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled.")
