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
