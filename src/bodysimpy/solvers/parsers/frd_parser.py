from pathlib import Path


def parse_max_abs_stress_component(
    path: str | Path,
    *,
    component: int,
) -> float:
    """Return the maximum absolute nodal stress component from an FRD file."""

    if component not in {1, 2, 3, 4, 5, 6}:
        raise ValueError("Stress component must be between 1 and 6.")

    frd_path = Path(path)

    in_stress_dataset = False
    stresses: list[float] = []

    for line in frd_path.read_text(encoding="utf-8").splitlines():
        columns = line.split()

        if not columns:
            continue

        if columns[0] == "-4":
            in_stress_dataset = len(columns) >= 2 and columns[1].upper() == "STRESS"
            continue

        if not in_stress_dataset:
            continue

        if columns[0] == "-3":
            in_stress_dataset = False
            continue

        if columns[0] not in {"-1", "-2"}:
            continue

        if len(columns) < 8:
            continue

        try:
            stress = float(columns[component + 1].replace("D", "E"))
        except ValueError:
            continue

        stresses.append(stress)

    if not stresses:
        raise ValueError("No STRESS dataset was found in the FRD file.")

    return max(abs(stress) for stress in stresses)
