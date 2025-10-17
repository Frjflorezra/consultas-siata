import json
from typing import Optional

import click

from app import App


@click.group()
@click.option("--config", "config_path", default="config.yaml", show_default=True, help="Ruta del archivo de configuración")
@click.pass_context
def cli(ctx: click.Context, config_path: str) -> None:
    ctx.obj = App(config_path=config_path)


@cli.command("listar")
@click.pass_obj
def listar(app: App) -> None:
    for ep in app.list_endpoints():
        params = ", ".join([p.get("name", "") for p in ep.params_spec]) if ep.params_spec else ""
        click.echo(f"- {ep.name} [{ep.method} {ep.path}] requires_params={ep.requires_params} params=[{params}]")


@cli.command("ejecutar")
@click.argument("endpoint", type=str)
@click.option("--param", "params", multiple=True, help="Parámetro en formato clave=valor (repetible)")
@click.option("--json", "as_json", is_flag=True, default=False, help="Imprimir respuesta en JSON")
@click.pass_obj
def ejecutar(app: App, endpoint: str, params: Optional[list[str]], as_json: bool) -> None:
    query = {}
    for p in params or []:
        if "=" not in p:
            raise click.UsageError("Usa --param clave=valor")
        k, v = p.split("=", 1)
        query[k] = v
    data = app.call_and_maybe_export(endpoint, params=query or None)
    if as_json:
        click.echo(json.dumps(data, ensure_ascii=False))
    else:
        click.echo("OK")


if __name__ == "__main__":
    cli()


