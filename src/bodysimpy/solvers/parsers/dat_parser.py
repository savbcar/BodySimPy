from pathlib import Path


def parse_tip_displacement(
    path: str | Path,
    *,
    tip_node_id: int,
    component: int = 3,
) -> float:
    """Extract a displacement component for the specified node."""

    if component not in {1, 2, 3}:
        raise ValueError("Displacement component must be 1, 2, or 3.")

    dat_path = Path(path)

    displacement: float | None = None

    for line in dat_path.read_text(encoding="utf-8").splitlines():
        columns = line.split()

        if len(columns) < 4:
            continue

        try:
            node_id = int(columns[0])
        except ValueError:
            continue

        if node_id != tip_node_id:
            continue

        try:
            components = [float(value.replace("D", "E")) for value in columns[1:4]]
        except ValueError:
            continue

        displacement = components[component - 1]

    if displacement is None:
        raise ValueError(f"No displacement result found for node {tip_node_id}.")

    return displacement


def parse_eigenfrequencies(
    path: str | Path,
) -> tuple[float, ...]:
    """Extract real eigenfrequencies in cycles per unit time from a CalculiX DAT file."""

    dat_path = Path(path)

    frequencies: list[float] = []
    in_eigenvalue_output = False

    for line in dat_path.read_text(encoding="utf-8").splitlines():
        normalized_line = "".join(line.upper().split())

        if "EIGENVALUEOUTPUT" in normalized_line:
            in_eigenvalue_output = True
            continue

        if not in_eigenvalue_output:
            continue

        columns = line.split()

        if not columns:
            if frequencies:
                break

            continue

        if len(columns) < 4:
            continue

        try:
            mode_number = int(columns[0])

            frequency_hz = float(
                columns[3].replace(
                    "D",
                    "E",
                )
            )

        except ValueError:
            continue

        if mode_number <= 0:
            continue

        if frequency_hz <= 0.0:
            continue

        frequencies.append(frequency_hz)

    if not frequencies:
        raise ValueError("No eigenfrequencies were found in the CalculiX DAT file.")

    return tuple(frequencies)
