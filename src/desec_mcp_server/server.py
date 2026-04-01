#!/usr/bin/env python3
"""
deSEC MCP Server — manage your deSEC.io DNS zones via MCP.

Entry point: desec-mcp-server
Env vars:
    DESEC_TOKEN  — your deSEC API token (required)
"""

import os
import json
import asyncio
import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

API_BASE = "https://desec.io/api/v1"


def _token() -> str:
    t = os.environ.get("DESEC_TOKEN", "")
    if not t:
        raise RuntimeError("DESEC_TOKEN environment variable is not set.")
    return t


def _headers() -> dict:
    return {
        "Authorization": f"Token {_token()}",
        "Content-Type": "application/json",
    }


def _get(path: str, params: dict | None = None):
    r = httpx.get(f"{API_BASE}{path}", headers=_headers(), params=params, timeout=15)
    r.raise_for_status()
    return r.json()


def _post(path: str, body: dict):
    r = httpx.post(f"{API_BASE}{path}", headers=_headers(), json=body, timeout=15)
    r.raise_for_status()
    return r.json()


def _patch(path: str, body: dict):
    r = httpx.patch(f"{API_BASE}{path}", headers=_headers(), json=body, timeout=15)
    r.raise_for_status()
    return r.json()


def _delete(path: str) -> None:
    r = httpx.delete(f"{API_BASE}{path}", headers=_headers(), timeout=15)
    r.raise_for_status()


def _get_text(path: str) -> str:
    r = httpx.get(f"{API_BASE}{path}", headers=_headers(), timeout=15)
    r.raise_for_status()
    return r.text


# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------

app = Server("desec-mcp-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="list_domains",
            description="List all domains on your deSEC account.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_domain",
            description="Get details of a specific domain.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Domain name (e.g. example.com)"},
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="create_domain",
            description="Register a new domain in deSEC.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Domain name to create"},
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="delete_domain",
            description="Delete a domain and all its DNS records from deSEC.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Domain name to delete"},
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="list_records",
            description=(
                "List all DNS records (RRsets) for a domain. "
                "Optionally filter by subname or type."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {"type": "string", "description": "Domain name"},
                    "subname": {
                        "type": "string",
                        "description": "Subname filter ('' for apex, 'www' for www.domain.com)",
                    },
                    "type": {
                        "type": "string",
                        "description": "Record type filter (A, AAAA, MX, CNAME, TXT, NS, SRV...)",
                    },
                },
                "required": ["domain"],
            },
        ),
        Tool(
            name="create_record",
            description="Create a DNS record (RRset) for a domain.",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {"type": "string"},
                    "subname": {
                        "type": "string",
                        "description": "Subname ('' for apex, 'www' for www.domain.com)",
                    },
                    "type": {
                        "type": "string",
                        "description": "Record type: A, AAAA, MX, CNAME, TXT, NS, SRV, CAA, TLSA...",
                    },
                    "records": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Record values (e.g. ['1.2.3.4'] for A, ['10 mail.example.com.'] for MX)",
                    },
                    "ttl": {
                        "type": "integer",
                        "description": "TTL in seconds (deSEC minimum is 3600 by default)",
                        "default": 3600,
                    },
                },
                "required": ["domain", "subname", "type", "records"],
            },
        ),
        Tool(
            name="update_record",
            description="Update (replace) an existing DNS record (RRset). All values are replaced.",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {"type": "string"},
                    "subname": {"type": "string", "description": "Subname ('' for apex)"},
                    "type": {"type": "string", "description": "Record type"},
                    "records": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "New record values (replaces all existing ones)",
                    },
                    "ttl": {"type": "integer", "description": "New TTL in seconds"},
                },
                "required": ["domain", "subname", "type", "records"],
            },
        ),
        Tool(
            name="delete_record",
            description="Delete a DNS record (RRset) from a domain.",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {"type": "string"},
                    "subname": {"type": "string", "description": "Subname ('' for apex)"},
                    "type": {"type": "string", "description": "Record type"},
                },
                "required": ["domain", "subname", "type"],
            },
        ),
        Tool(
            name="list_tokens",
            description="List API tokens on the account.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="create_token",
            description="Create a new API token, optionally restricted to a single domain.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Human-readable name for the token"},
                    "domain": {
                        "type": "string",
                        "description": "Optional: restrict this token to the given domain only",
                    },
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="delete_token",
            description="Delete an API token by its ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "token_id": {"type": "string", "description": "Token UUID"},
                },
                "required": ["token_id"],
            },
        ),
        Tool(
            name="export_zonefile",
            description="Export the full zone as a standard RFC 1035 zone file.",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {"type": "string", "description": "Domain name"},
                },
                "required": ["domain"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        result = _dispatch(name, arguments)
        return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
    except httpx.HTTPStatusError as e:
        err = {"error": f"HTTP {e.response.status_code}", "detail": e.response.text}
        return [TextContent(type="text", text=json.dumps(err, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]


def _dispatch(name: str, args: dict):
    # --- Domains ---
    if name == "list_domains":
        return _get("/domains/")

    if name == "get_domain":
        return _get(f"/domains/{args['name']}/")

    if name == "create_domain":
        return _post("/domains/", {"name": args["name"]})

    if name == "delete_domain":
        _delete(f"/domains/{args['name']}/")
        return {"status": "deleted", "domain": args["name"]}

    # --- Records ---
    if name == "list_records":
        params = {}
        if "subname" in args:
            params["subname"] = args["subname"]
        if "type" in args:
            params["type"] = args["type"]
        return _get(f"/domains/{args['domain']}/rrsets/", params=params or None)

    if name == "create_record":
        body = {
            "subname": args["subname"],
            "type": args["type"],
            "records": args["records"],
            "ttl": args.get("ttl", 3600),
        }
        return _post(f"/domains/{args['domain']}/rrsets/", body)

    if name == "update_record":
        subname = args["subname"] or "@"
        body: dict = {"records": args["records"]}
        if "ttl" in args:
            body["ttl"] = args["ttl"]
        return _patch(f"/domains/{args['domain']}/rrsets/{subname}/{args['type']}/", body)

    if name == "delete_record":
        subname = args["subname"] or "@"
        _delete(f"/domains/{args['domain']}/rrsets/{subname}/{args['type']}/")
        return {"status": "deleted"}

    # --- Tokens ---
    if name == "list_tokens":
        return _get("/auth/tokens/")

    if name == "create_token":
        body = {"name": args["name"]}
        if "domain" in args:
            body["domain_policies"] = [{"domain": args["domain"], "perm_write": True}]
        return _post("/auth/tokens/", body)

    if name == "delete_token":
        _delete(f"/auth/tokens/{args['token_id']}/")
        return {"status": "deleted", "token_id": args["token_id"]}

    # --- Zonefile ---
    if name == "export_zonefile":
        return {"zonefile": _get_text(f"/domains/{args['domain']}/zonefile/")}

    return {"error": f"Unknown tool: {name}"}


# ---------------------------------------------------------------------------
# Entry point — stdio_server is an async context manager, not a coroutine
# ---------------------------------------------------------------------------

async def _run():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


def main():
    asyncio.run(_run())


if __name__ == "__main__":
    main()
