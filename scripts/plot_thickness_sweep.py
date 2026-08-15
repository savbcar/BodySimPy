import matplotlib.pyplot as plt
import pandas as pd


def main() -> None:
    dataframe = pd.read_csv("docs/validation/thickness_sweep.csv")

    plt.figure(figsize=(8, 5))

    plt.plot(
        dataframe["thickness_mm"],
        dataframe["max_stress_mpa"],
        marker="o",
    )

    plt.xlabel("Wall thickness [mm]")
    plt.ylabel("Maximum axial stress [MPa]")
    plt.title("BodySimPy Thickness Sweep — Stress")

    plt.grid(True)
    plt.tight_layout()

    plt.savefig(
        "docs/figures/thickness_vs_stress.png",
        dpi=200,
    )

    plt.close()


if __name__ == "__main__":
    main()
