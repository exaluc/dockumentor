{% for service_name, details in services.items() %}
### 🐳 Service: {{ service_name }}
- **Image**: {{ details.image }}
- **Ports**: {% for port in details.ports %}{{ port }}{% if not loop.last %}, {% endif %}{% endfor %}
- **Volumes**: {% for volume in details.volumes %}{{ volume }}{% if not loop.last %}, {% endif %}{% endfor %}
- **Depends On**: {% for dependency in details.depends_on %}{{ dependency }}{% if not loop.last %}, {% endif %}{% endfor %}
- **Command**: {{ details.command }}
#### Environment Variables

| Variable | Value |
|----------|-------|{% for key, value in details.environment.items() %}
| {{ key }} | {{ value }} |{% endfor %}
{% endfor %}


## Networks

{% for network, details in networks.items() %}
### Network: {{ network }}

{% endfor %}

## Graphs

### Network depend
```mermaid
{{ mermaid_diagram }}
```

### Services depend
```mermaid
sankey-beta
{{ sankey_diagram_depends }}
```

### Services ports
```mermaid
sankey-beta
{{ sankey_diagram_network }}
```

## Service Interaction Sequence Diagram

```mermaid
{{ sequence_diagram }}
```

## Example Commands

- **Start Services**: `{{ example_commands.start }}`
- **Stop Services**: `{{ example_commands.stop }}`
- **View Logs for a Service**: `{{ example_commands.view_logs }}`

## Troubleshooting

{% for issue in troubleshooting %}
- {{ issue }}
{% endfor %}

## Maintenance Tips

{% for tip in maintenance_tips %}
- {{ tip }}
{% endfor %}