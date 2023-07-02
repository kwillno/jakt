import click
from datetime import datetime
from jakt.jakt import _jakt, JaktError, JaktActiveError, JaktNotActiveError


@click.group()
@click.version_option(version="0.0.1", prog_name="jakt")
@click.pass_context
def cli(ctx):
    """Jakt is just another (k)ommandline timetracker.

    Jakt helps you keep track of how you spend your time.
    Whether you want to keep better track of how much time
    you spend on each project or want to keep yourself
    accountable while working, jakt is the perfect tool."""

    ctx.ensure_object(dict)
    ctx.obj['jakt'] = _jakt()
    


@cli.command()
@click.argument("project")
@click.argument("tags", nargs = -1)
@click.pass_context
def start(ctx, project, tags):
    """Start a new timeslot"""
    jkt = ctx.obj['jakt']

    try:
        response = jkt.start(project=project, tags=tags)

        hrStart = datetime.fromtimestamp(response["start"]).strftime('%H:%M')
        tags = response["tags"]

        click.echo(f"{project} started at {hrStart}.")
        click.echo(f"Tags: {' '.join(str(t) for t in tags)}")


    except JaktActiveError:

        click.echo("Other timer already running.")
        ctx.invoke(status)

@cli.command()
@click.pass_context
def stop(ctx):
    """Stops current project"""
    jkt = ctx.obj['jakt']

    try:
        response = jkt.stop()

        project = response["project"]
        hrStart = datetime.fromtimestamp(response["start"]).strftime('%H:%M')
        hrStop  = datetime.fromtimestamp(response["end"]).strftime('%H:%M')
        tags = response["tags"]

        click.echo(f"{project} stopped at {hrStop}.")
        click.echo(f"Tags: {' '.join(str(t) for t in tags)}")
        click.echo(f"Timer ran for {response['elapsedHour']:02}:{response['elapsedMin']:02}")

    except JaktNotActiveError:
        click.echo("No timer started.")


@cli.command()
@click.pass_context
def status(ctx):
    """Displays current status"""
    jkt = ctx.obj['jakt']

    try:
        response = jkt.status()

        project = response["project"]
        hrStart = datetime.fromtimestamp(response["start"]).strftime('%H:%M')
        tags = response["tags"]

        click.echo(f"{project} started at {hrStart}.")
        click.echo(f"Tags: {' '.join(str(t) for t in tags)}")
        click.echo(f"Runtime is {response['elapsedHour']:02}:{response['elapsedMin']:02}")

    except JaktNotActiveError:
        click.echo("No timer started.")


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

'''@click.option(
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
@click.option("-t", "--tags", is_flag=True, default=False, help="Display tags")'''
@cli.command()
@click.pass_context
def add(ctx):
    """Add a timeslot that was not logged live"""
    jkt = ctx.obj['jakt']

    jkt.add()
    


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
    cli(obj={})
