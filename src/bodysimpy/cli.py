import typer

app = typer.Typer(
    name="bodysim",
    help="Structural CAE workflow automation for automotive body structures.",
    no_args_is_help=True,
)


@app.command()
def version() -> None:
    """Show the installed BodySimPy version."""

    typer.echo("BodySimPy 0.1.0")


if __name__ == "__main__":
    app()
