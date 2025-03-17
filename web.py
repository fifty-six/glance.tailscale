from sys import stderr
from datetime import datetime, timezone
from operator import attrgetter as attr

import httpx
import os

from jinja2 import Environment, FileSystemLoader

import quart
from quart import Quart, request
from quart.helpers import make_response
from quart_schema import QuartSchema, validate_querystring

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

app = Quart(__name__)
schema = QuartSchema(app)

env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("device.jinja")

key = os.environ.get("TS_AUTH_KEY")
if not key:
    print("Missing env variable $TS_AUTH_KEY!", file=stderr)
    exit(-1)

ts_client = httpx.AsyncClient(headers={"Authorization": f"Bearer {key}"})

class Device(BaseModel):
    model_config = ConfigDict(  # pyright: ignore[reportUnannotatedClassAttribute]
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    last_seen: datetime
    addresses: list[str]
    hostname: str
    name: str
    os: str
    update_available: bool

    @property
    def ipv4(self) -> str:
        return self.addresses[0]

    @property
    def machine_name(self) -> str:
        return self.name.split(".")[0]

    @property
    def alive(self) -> bool:
        return abs((self.last_seen - datetime.now(timezone.utc)).total_seconds()) < 5

    @property
    def last_seen_fmt(self) -> str:
        return self.last_seen.strftime("%b %d, %Y")


class Devices(BaseModel):
    devices: list[Device]

class Query(BaseModel):
    show_update: bool | None = False
    show_status: bool | None = True

@app.route("/")
@validate_querystring(Query)
async def tailscale(query_args: Query) -> quart.typing.ResponseTypes:
    req = await ts_client.get("https://api.tailscale.com/api/v2/tailnet/-/devices")
    ts = Devices.model_validate(req.json())

    rendered = template.render(
        devices=sorted(ts.devices, key=attr("last_seen"), reverse=True),
        show_update=query_args.show_update,
        show_status=query_args.show_status,
    )

    response = await make_response(rendered)
    response.headers["Widget-Title"] = "Tailscale"
    response.headers["Widget-Content-Type"] = "html"

    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0")
