import click


@click.group()
@click.version_option(version="0.0.1", prog_name="Jakt")
def cli():
    """JAKT is just another (k)ommandline timetracker."""
    pass


@cli.command()
@click.argument("project")
def start(project):
    """Start a new timeslot"""
    click.echo(f"Project: {project}")


@cli.command()
def stop():
    """Stops current project"""
    pass


@cli.command()
def status():
    """Displays current status"""
    pass


@cli.command()
@click.option(
    "-t",
    "--to",
    "to",
    type=click.DateTime(formats=["%d-%m-%Y %H:%M:%S", "%H:%M:%S"]),
    help="Starttime of search period",
)
@click.option(
    "-f",
    "--from",
    "from_",
    type=click.DateTime(formats=["%d-%m-%Y %H:%M:%S", "%H:%M:%S"]),
    help="Endtime of search period",
)
@click.option(
    "-c", "--categories", is_flag=True, default=False, help="Display categories"
)
@click.option("-p", "--projects", is_flag=True, default=False, help="Display projects")
@click.option("-t", "--tags", is_flag=True, default=False, help="Display tags")
@click.option("-s", "--timeslots", is_flag=True, default=True, help="Display timeslots")
def ls(to, from_, categories, projects, tags, timeslots):
    """Lists timeslots"""
    if from_ and to:
        click.echo(f"From {from_} to {to}")

    elif bool(from_) ^ bool(to):
        click.echo("Both -t/--to and -f/--from need to be set")

    else:
        click.echo(f"Lists default timeslots")


@cli.command()
@click.option(
    "-t",
    "--to",
    "to",
    type=click.DateTime(formats=["%d-%m-%Y %H:%M:%S", "%H:%M:%S"]),
    help="Starttime of search period",
)
@click.option(
    "-f",
    "--from",
    "from_",
    type=click.DateTime(formats=["%d-%m-%Y %H:%M:%S", "%H:%M:%S"]),
    help="Endtime of search period",
)
@click.option(
    "-c", "--categories", is_flag=True, default=False, help="Display categories"
)
@click.option("-p", "--projects", is_flag=True, default=False, help="Display projects")
@click.option("-t", "--tags", is_flag=True, default=False, help="Display tags")
def add(to, from_, categories, projects, tags):
    """Add a timeslot that was not logged live"""
    pass


@cli.command()
@click.argument("index")
def edit(index):
    """Edits categories, projects, tags and timeslots"""
    pass


@cli.command()
def report():
    """Generates reports from timetracker data"""
    pass


@cli.command()
def pause():
    """Takes a break in current timeslot"""
    pass


@cli.command()
def resume():
    """Resumes paused timeslot"""
    pass


@cli.command()
def config():
    """Sets new values in configuration file"""
    pass


@cli.command()
def sync():
    """Syncronizes data with server"""


if __name__ == "__main__":
    cli()
