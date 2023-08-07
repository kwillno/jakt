import click
from datetime import datetime

from .__init__ import jakt
from .timeslot import timeslot
from .exceptions import *


@click.group()
@click.version_option(version="0.0.5", prog_name="jakt")
@click.pass_context
def cli(ctx):
    """Jakt is just another (k)ommandline timetracker.

    Jakt helps you keep track of how you spend your time.
    Whether you want to keep better track of how much time
    you spend on each project or want to keep yourself
    accountable while working, jakt is the perfect tool."""

    ctx.ensure_object(dict)
    ctx.obj["jakt"] = jakt()

    if ctx.obj["jakt"].getConfig()['debug']:
        click.echo("Debug mode is enabled")


@cli.command()
@click.argument("project")
@click.argument("tags", nargs=-1)
@click.pass_context
def start(ctx, project, tags):
    """Start a new timeslot"""
    jkt = ctx.obj["jakt"]

    try:
        response = jkt.start(project=project, tags=tags)

        project = click.style(response.project, fg="blue", bold=True)
        hrStart = click.style(
            datetime.fromtimestamp(response.start).strftime("%H:%M"),
            fg="red",
            bold=True,
        )
        tags = click.style(" ".join(str(t) for t in response.tags), fg="green")

        click.echo(f"{project} started at {hrStart}")
        click.echo(f"Tags: {tags}")

    except JaktActiveError:
        click.echo("Other timer already running")
        ctx.invoke(status)


@cli.command()
@click.pass_context
def stop(ctx):
    """Stops current project"""
    jkt = ctx.obj["jakt"]

    try:
        ts = jkt.stop()

        project = click.style(ts.project, fg="blue", bold=True)
        tags = click.style(" ".join(str(t) for t in ts.tags), fg="green")

        hrStop = click.style(ts.end_dt.strftime("%H:%M"), fg="red", bold=True)
        dur = ts.getDurationHR()
        runtime = click.style(f"{dur['hh']:02}:{dur['M']:02}", fg="green", bold=True)

        click.echo(f"{project} stopped at {hrStop}")
        click.echo(f"Tags: {tags}")
        click.echo(f"Timer ran for {runtime}")

    except JaktNotActiveError:
        click.echo("No timer started.")


@cli.command()
@click.pass_context
def status(ctx):
    """Displays current status"""
    jkt = ctx.obj["jakt"]

    try:
        response = jkt.status()

        project = click.style(response["project"], fg="blue", bold=True)
        hrStart = click.style(
            datetime.fromtimestamp(response["start"]).strftime("%H:%M"),
            fg="red",
            bold=True,
        )
        tags = click.style(" ".join(str(t) for t in response["tags"]), fg="green")
        runtime = click.style(
            f"{response['elapsedHour']:02}:{response['elapsedMin']:02}",
            fg="green",
            bold=True,
        )

        click.echo(f"{project} started at {hrStart}.")
        click.echo(f"Tags: {tags}")
        click.echo(f"Runtime is {runtime}")

    except JaktNotActiveError:
        click.echo("No timer started.")


@cli.command()
@click.option(
    "--to",
    "to",
    type=click.DateTime(formats=["%d-%m-%y"]),
    help="Starttime of search period",
)
@click.option(
    "--from",
    "from_",
    type=click.DateTime(formats=["%d-%m-%y"]),
    help="Endtime of search period",
)
@click.option(
    "-c", "--categories", is_flag=True, default=False, help="Display categories"
)
@click.option("-p", "--projects", is_flag=True, default=False, help="Display projects")
@click.option("-t", "--tags", is_flag=True, default=False, help="Display tags")
# TODO: Display all timeslots using -a
@click.pass_context
def ls(ctx, to, from_, categories, projects, tags):
    """Lists timeslots and other data"""
    jkt = ctx.obj["jakt"]

    if categories:
        categories = jkt.getCategories()

        for cat in categories:
            click.echo(f"{click.style(cat, fg='red', bold=True)}")

        return

    if projects:
        projects = jkt.getProjects()

        for project in projects:
            click.echo(f"{click.style(project, fg='blue', bold=True)}")

        return

    if tags:
        tags = jkt.getTags()

        for tag in tags:
            click.echo(f"{click.style(tag, fg='green')}")

        return

    if from_ or to:
        # A few cases of input sanitation
        if from_ and (not to):
            to = datetime.now()

        elif to and (not from_):
            click.echo("--from must be set if --to is set")
            return

        if from_ > to:
            # Switch the parameters if they are given in the wrong order
            a = from_
            from_ = to
            to = a
            click.echo("--to/--from in wrong order. Flipping them.")

        timeslots = jkt.getTimeslots(to, from_)
    else:
        timeslots = jkt.getTimeslots()

    # Want timeslots sorted chronologically
    timeslots.reverse()

    for i in range(len(timeslots)):
        if i == 10:
            click.echo(f"{len(timeslots)-i} timeslots not shown.")
            break

        ts = timeslots[i]

        # Define all styles and shown data
        ts_id = click.style(ts.id, fg="yellow")
        ts_project = click.style(ts.project, fg="blue", bold=True)

        # Make sure time is readable and makes sense
        ts_start = ts.start_dt
        ts_end = ts.end_dt

        if ts_start.date() == ts_end.date():
            ts_start_hr = ts_start.strftime("%H:%M")
        else:
            ts_start_hr = ts_start.strftime("%H:%M %d-%m-%y")

        ts_end_hr = ts_end.strftime("%H:%M %d-%m-%y")

        s = str(ts.duration).split(":")
        ts_duration = click.style(
            f"{int(s[0]):02}:{int(s[1]):02}:{int(s[2]):02}", fg="green"
        )

        ts_tags = click.style(" ".join(str(t) for t in ts.tags), fg="green")

        # Display data on single line
        click.echo(
            f"{ts_id} {ts_duration} ({ts_start_hr} - {ts_end_hr}) {ts_project} {ts_tags}"
        )


@cli.command()
@click.option(
    "--to",
    "to",
    type=click.DateTime(formats=["%d-%m-%y %H:%M", "%d-%m-%y %H:%M:%S"]),
    help="Starttime",
    required=True,
)
@click.option(
    "--from",
    "from_",
    type=click.DateTime(formats=["%d-%m-%y %H:%M", "%d-%m-%y %H:%M:%S"]),
    help="Endtime",
    required=True,
)
@click.argument("project")
@click.argument("tags", nargs=-1)
@click.pass_context
def add(ctx, to, from_, project, tags):
    """Add a timeslot that was not logged live"""
    jkt = ctx.obj["jakt"]

    ts = timeslot(
        ID=jkt.generateUniqueID(),
        start=int(from_.strftime("%s")),
        end=int(to.strftime("%s")),
        project=project,
        tags=tags,
    )

    jkt.add(ts)


"""
@cli.command()
@click.argument("index")
def edit(index):
    # Edits categories, projects, tags and timeslots
    pass
"""


@cli.command()
@click.option("-p", "--project", default="", help="Show only specified project")
@click.option("-t", "--tag", default="", help="Show only specified tag")
@click.pass_context
def report(ctx, project, tag):
    """Generates reports from timetracker data"""
    jkt = ctx.obj["jakt"]

    jkt_report = jkt.report()

    if project:
        projects = jkt_report.getProjectReport(project=project)
    else:
        projects = jkt_report.getProjectReport()

    for project in projects:
        hrProject = click.style(project["project"], fg="blue", bold=True)
        hrTime = click.style(project["time"], fg="red", bold=True)
        click.echo(f"{hrProject}  {hrTime}")

        tags = jkt_report.getTagReport(project["project"])
        for tag in tags:
            hrTag = click.style(tag["tag"], fg="green", bold=True)
            hrTagTime = click.style(tag["time"], fg="yellow")

            click.echo(f" - {hrTag}  {hrTagTime}")



@cli.command()
@click.pass_context
def resume(ctx):
    """
    Start new timeslot with same settings
    """
    jkt = ctx.obj["jakt"]

    try:
        response = jkt.resume()

        project = click.style(response.project, fg="blue", bold=True)
        hrStart = click.style(
            datetime.fromtimestamp(response.start).strftime("%H:%M"),
            fg="red",
            bold=True,
        )
        tags = click.style(" ".join(str(t) for t in response.tags), fg="green")

        click.echo(f"{project} started at {hrStart}")
        click.echo(f"Tags: {tags}")

    except JaktActiveError:
        click.echo("Other timer already running")
        ctx.invoke(status)

@cli.command()
@click.argument("key", required=False)
@click.argument("value", required=False)
@click.pass_context
def config(ctx, key:str = None, value:str = None):
    """
    Interacts with config
    """
    jkt = ctx.obj["jakt"]

    config = jkt.getConfig()

    # If key and value are set
    # change or add this in config
    if key and value:
        if value.lower() == 'false':
            config[key] = False
        elif value.lower() == 'true':
            config[key] = True
        else:
            config[key] = value

        try:
            jkt.putConfig(config)

        except JaktError:
            click.echo("An error has occured.")

    else:
        click.echo(config)


@cli.command()
@click.argument("state", type=bool, required=False)
@click.pass_context
def debug(ctx, state: bool = None):
    """
    Enables and disables debug mode
    """
    jkt = ctx.obj["jakt"]

    config = jkt.getConfig()
        
    if state != None:
        config['debug'] = state

    else:
        if config['debug']:
            config['debug'] = False
        else:
            config['debug'] = True
            
    jkt.putConfig(config)

    config = jkt.getConfig()
    if config['debug']:
        click.echo("Debug mode has been enabled!")
    else:
       click.echo("Debug mode has been disbled!")

"""
@cli.command()
def config():
    # Sets new values in configuration file
    pass


@cli.command()
def sync():
    # Syncronizes data with server
    pass

@cli.command()
def license():
    # Outputs license
    pass
"""

if __name__ == "__main__":
    cli(obj={})
