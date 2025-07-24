import click
from ...infrastructure import Container
from .application import CLIApplication


@click.command()
def main() -> None:
    """EBS Snapshot CLI Tool - Clean Architecture Entry Point"""
    container = Container()
    app = CLIApplication(container)
    app.run()


if __name__ == "__main__":
    main()
