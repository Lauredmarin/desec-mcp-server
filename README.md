# desec-mcp-server

Serveur MCP pour gérer vos zones DNS [deSEC.io](https://desec.io) — installable en une commande via `uvx`.

## Démarrage rapide avec `uvx`

Ajoute ceci dans ton fichier de config MCP (ex : `claude_desktop_config.json`) :

```json
{
  "mcpServers": {
    "desec": {
      "type": "STDIO",
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/Lauredmarin/desec-mcp-server.git",
        "desec-mcp-server"
      ],
      "env": {
        "DESEC_TOKEN": "votre_token_desec"
      }
    }
  }
}
```

> **Token deSEC** : récupère-le sur https://desec.io → *Account* → *Token Management*

### Emplacement du fichier de config

| OS      | Chemin |
|---------|--------|
| macOS   | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Linux   | `~/.config/Claude/claude_desktop_config.json` |

---

## Installation alternative (pip)

```bash
pip install git+https://github.com/Lauredmarin/desec-mcp-server.git
export DESEC_TOKEN="votre_token"
desec-mcp-server
```

---

## Outils disponibles

| Outil | Description |
|-------|-------------|
| `list_domains` | Lister tous les domaines du compte |
| `get_domain` | Détails d'un domaine |
| `create_domain` | Créer un nouveau domaine |
| `delete_domain` | Supprimer un domaine |
| `list_records` | Lister les enregistrements DNS (filtre par subname/type possible) |
| `create_record` | Créer un enregistrement DNS |
| `update_record` | Mettre à jour un enregistrement DNS |
| `delete_record` | Supprimer un enregistrement DNS |
| `list_tokens` | Lister les tokens API |
| `create_token` | Créer un token API (optionnellement restreint à un domaine) |
| `delete_token` | Supprimer un token API |
| `export_zonefile` | Exporter la zone au format RFC 1035 |

---

## Exemples de prompts

Une fois connecté dans Claude Desktop :

- *"Liste mes domaines deSEC"*
- *"Ajoute un enregistrement A pour `www.mondomaine.com` pointant vers `1.2.3.4`"*
- *"Montre-moi tous les enregistrements MX de `mondomaine.com`"*
- *"Exporte le zonefile de `mondomaine.com`"*
- *"Crée un token API limité au domaine `mondomaine.com`"*

---

## Notes importantes

- Le TTL minimum chez deSEC est **3600 secondes** (1h) par défaut.
- deSEC impose une limite de **300 modifications** d'enregistrements par jour et par domaine.
- Le secret d'un token n'est affiché **qu'une seule fois** à la création — conserve-le.
- DNSSEC est activé **automatiquement** sur tous les domaines deSEC.
