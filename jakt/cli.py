import click
from datetime import datetime

from .__init__ import jakt
from .timeslot import timeslot
from .exceptions import *


@click.group()
@click.version_option(version="0.0.7", prog_name="jakt (dev)")
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
    "-c",
    "--category", 
    is_flag=True, 
    default=False, 
    help="Display categories"
)
@click.option("-p", "--projects", is_flag=True, default=False, help="Display projects")
@click.option("-t", "--tags", is_flag=True, default=False, help="Display tags")
@click.option("-a", "--all", "_all" ,is_flag=True, default=False, help="Display all elements")
@click.pass_context
def ls(ctx, to, from_, category, projects, tags, _all):
    """Lists timeslots and other data"""
    jkt = ctx.obj["jakt"]

    if category:
        categories = jkt.getCategories()

        for i in range(len(categories)):
            if i == 10 and not _all:
                click.echo(f"{len(categories)-i} categories not shown.")
                break
            click.echo(f"{click.style(categories[i], fg='red', bold=True)}")

        return

    if projects:
        projects = jkt.getProjects()

        for i in range(len(projects)):
            if i == 10 and not _all:
                click.echo(f"{len(projects)-i} projects not shown.")
                break
            click.echo(f"{click.style(projects[i], fg='blue', bold=True)}")

        return

    if tags:
        tags = jkt.getTags()

        for i in range(len(tags)):
            if i == 10 and not _all:
                click.echo(f"{len(tags)-i} tags not shown.")
                break
            click.echo(f"{click.style(tags[i], fg='green')}")

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
        if i == 10 and not _all:
            click.echo(f"{len(timeslots)-i} timeslots not shown.")
            break

        ts = timeslots[i]

        click.echo(ts.toHR())


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


@cli.command()
@click.argument("id")
@click.option(
    "-s",
    "--start",
    "start",
    type=click.DateTime(formats=["%d-%m-%y %H:%M"]),
    help="Starttime",
    default=None,
)
@click.option(
    "-e",
    "--end",
    "end",
    type=click.DateTime(formats=["%d-%m-%y %H:%M"]),
    help="Endtime",
    default=None,
)
@click.option(
    "-p",
    "--project",
    "project",
    help="Project name",
    default=None,
)
@click.option(
    "-t",
    "--tag",
    "tags",
    multiple=True, 
    help="Tag, can be used multiple times",
    default=None,
)
@click.pass_context
def edit(ctx, id, start, end, project, tags):
    """
    Edits timeslots. \n
    The given timeslot is the baseline and modified with the changes given in this command.
    """
    jkt = ctx.obj["jakt"]

    ts = jkt.getTimeslot(queryId=id)
    
    # Get all parameters current for matching timeslot 
    newStart = ts.start
    newEnd = ts.end
    newProject = ts.project
    newTags = ts.tags

    # Update given fields
    if start is not None:
        newStart = int(start.timestamp())

    if end is not None:
        newEnd = int(end.timestamp())

    if project is not None:
        newProject = project

    if tags != ():
        newTags = list(tags)

    # Initialize new timeslot
    newTS = timeslot(
            ID = id,
            start = newStart,
            end = newEnd,
            project = newProject,
            tags = newTags,
        )

    # Update the entry in data
    jkt.editTimeslot(queryId=id, ts=newTS)

    # Print the updated timeslot
    click.echo(newTS.toHR())



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

        if tag:
            tgs = jkt_report.getTagReport(project["project"], tag=tag)
        else:
            tgs = jkt_report.getTagReport(project["project"])

        if len(tgs)>0:
            click.echo(f"{hrProject}  {hrTime}")

        for tg in tgs:
            hrTag = click.style(tg["tag"], fg="green", bold=True)
            hrTagTime = click.style(tg["time"], fg="yellow")

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


@cli.command()
@click.argument("path", type=str, required=False, default=None)
@click.pass_context
def export(ctx, path):
    """
    Exports all timeslots to given .csv file
    """
    jkt = ctx.obj["jakt"]

    try:
        jkt.export(path=path)
    except JaktPathError as e:
        click.echo(f"JaktPathError: {e}")


@cli.command()
@click.argument("path", type=str, required=False, default=None)
@click.option("-f", "--format","_format", default="jakt", help="Format of the file you are trying to import")
@click.pass_context
def source(ctx, path, _format):
    """
    Imports timeslots from given .csv file
    """
    jkt = ctx.obj["jakt"]

    try:
        if _format != "jakt":
            jkt.importTT(path=path)
            return
        
        jkt.importInternal(path=path, _format=_format)

    except JaktPathError as e:
        click.echo(f"JaktPathError: {e}")


@cli.command()
@click.pass_context
def path(ctx):
    """
    Returns path of stored data
    """
    jkt = ctx.obj["jakt"]

    pathString = jkt.getPath()

    # Escape whitespace in string
    pathString = pathString.replace(" ", "\ ")

    click.echo("Your jakt data is stored at:")
    click.echo(pathString)

"""
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
