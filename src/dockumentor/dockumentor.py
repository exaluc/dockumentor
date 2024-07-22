import os
import yaml
import click
from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateNotFound
import re

DOCKUMENTOR_START_TAG = "<!-- DOCKUMENTOR START -->"
DOCKUMENTOR_END_TAG = "<!-- DOCKUMENTOR END -->"

def sanitize_for_mermaid_id(text):
    """Sanitize the text to create valid IDs for Mermaid diagrams."""
    text = text.replace(r"\|", "_")
    return re.sub(r'[^a-zA-Z0-9À-ÿ]', '_', text)

def load_yaml_file(filepath):
    """Loads a YAML file with support for advanced features."""
    with open(filepath, 'r', encoding='utf-8') as file:
        return yaml.load(file, Loader=yaml.FullLoader)

def render_template(template_name, output_path, context, append=False):
    """Renders a Jinja2 template and writes it to an output file."""
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    
    try:
        template = env.get_template(template_name)
    except TemplateNotFound:
        print(f"Template not found: {template_name}. Looking in directory: {template_dir}")
        raise

    content = f"{DOCKUMENTOR_START_TAG}\n{template.render(context)}\n{DOCKUMENTOR_END_TAG}"

    if append and os.path.exists(output_path):
        with open(output_path, 'r', encoding='utf-8') as file:
            existing_content = file.read()

        if DOCKUMENTOR_START_TAG in existing_content and DOCKUMENTOR_END_TAG in existing_content:
            start_index = existing_content.index(DOCKUMENTOR_START_TAG)
            end_index = existing_content.index(DOCKUMENTOR_END_TAG) + len(DOCKUMENTOR_END_TAG)
            new_content = existing_content[:start_index] + content + existing_content[end_index:]
        else:
            new_content = existing_content + '\n\n' + content
    else:
        new_content = content

    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(new_content)
    
    print(f"Documentation generated at: {output_path}")

def normalize_environment(env_var):
    """Converts list of environment variables to a dictionary if needed."""
    if isinstance(env_var, list):
        env_dict = {}
        for item in env_var:
            if '=' in item:
                key, value = item.split('=', 1)
                env_dict[key] = value
        return env_dict
    elif isinstance(env_var, dict):
        return env_var
    return {}

def parse_ports(service_details):
    """Parse and format port configurations to handle multiple formats, including IP:port:port and exposed ports."""
    parsed_ports = []
    if 'ports' in service_details:
        for port in service_details['ports']:
            parts = port.split(':')
            if len(parts) == 3:  # IP:port:port format
                ip, start_port, end_port = parts
                parsed_ports.append(f"{ip}:{start_port}:{end_port}")
            elif len(parts) == 2:
                # When no IP is specified, assume '0.0.0.0' for external accessibility
                if re.match(r'\d+\.\d+\.\d+\.\d+', parts[0]):  # Explicit IP:port format
                    parsed_ports.append(port)
                else:
                    # Treat as external by default when only two parts without explicit IP
                    parsed_ports.append(f"0.0.0.0:{parts[0]}:{parts[1]}")
            else:
                # Single port number, assume external on all interfaces
                parsed_ports.append(f"0.0.0.0:{port}:{port}")
    if 'expose' in service_details:
        for port in service_details['expose']:
            parsed_ports.append(f"internal:{port}:{port}")
    return parsed_ports


def generate_mermaid_diagram(services, networks):
    """Generates a Mermaid diagram from Docker Compose service data."""
    mermaid_data = "flowchart TD\n"
    for service_name, details in services.items():
        ports = parse_ports(details)
        node_label = f"{service_name}<br>{details.get('image', 'No image specified')}"
        node_label += "<br>Ports: " + ', '.join(ports) if ports else ""
        mermaid_data += f"{sanitize_for_mermaid_id(service_name)}[\"{node_label}\"]\n"
        if 'depends_on' in details:
            for dependency in details['depends_on']:
                mermaid_data += f"{sanitize_for_mermaid_id(dependency)} --> {sanitize_for_mermaid_id(service_name)}\n"
    for network_name in networks:
        mermaid_data += f"subgraph {network_name}\n"
        for service_name, details in services.items():
            if network_name in details.get('networks', []):
                mermaid_data += f"{sanitize_for_mermaid_id(service_name)}\n"
        mermaid_data += "end\n"
    return mermaid_data

def generate_sankey_diagram_network(services, networks):
    """Generates a Mermaid Sankey diagram from Docker Compose service data focusing on network ports."""
    connections = set()  # Use a set to avoid duplicates
    for service_name, details in services.items():
        parsed_ports = parse_ports(details)
        service_name_with_ports = f"{sanitize_for_mermaid_id(service_name)}"

        # Check if the service has explicitly exposed ports
        if parsed_ports:
            for port in parsed_ports:
                if "internal" in port:
                    # Internal port binding (accessible only within the host)
                    port_details = port.replace("internal:", "Internal: ")
                    connections.add(f"Internal, {service_name_with_ports}, 1")
                else:
                    # External port binding (accessible from outside the host)
                    port_details = port.replace("0.0.0.0", "External") if "0.0.0.0" in port else port
                    connections.add(f"External, {service_name_with_ports}, 1")
        else:
            # Handle cases where services have no specific ports exposed
            network_association = '; '.join(details.get('networks', []))
            if network_association:
                connections.add(f"{network_association}, {service_name_with_ports}, 1")
            else:
                # Indicate that there is no network defined for the service
                connections.add(f"No Network, {service_name_with_ports}, 1")

    # Convert set of connections to a sorted list and join with new lines
    formatted_connections = "\n".join(sorted(connections))
    return formatted_connections

def generate_sankey_diagram_depends(services, networks):
    """Generates a Mermaid Sankey diagram from Docker Compose service data focusing on service dependencies and network isolation."""
    connections = set()  # Use a set to avoid duplicates
    for service_name, details in services.items():
        service_ports = parse_ports(details)
        service_port_details = "; ".join(service_ports).replace(",", ";") if service_ports else ""
        service_name_with_ports = f"{sanitize_for_mermaid_id(service_name)}"
        networks_assigned = details.get('networks', [])

        # Handle service dependencies
        depends_on_services = details.get('depends_on', [])
        if depends_on_services:
            for dependency in depends_on_services:
                if isinstance(dependency, dict):  # Handling cases where depends_on could be a YAML reference
                    dependency_name = list(dependency.keys())[0]  # Assuming single key dict for dependency name
                    dependency_ports = parse_ports(services[dependency_name])
                else:
                    dependency_name = dependency
                    dependency_ports = parse_ports(services[dependency])

                dependency_port_details = "; ".join(dependency_ports).replace(",", ";") if dependency_ports else ""
                dependency_name_with_ports = f"{sanitize_for_mermaid_id(dependency_name)}"
                connection = f"{dependency_name_with_ports}, {service_name_with_ports}, 1"
                connections.add(connection)

    # Convert set of connections to a sorted list and join with new lines
    formatted_connections = "\n".join(sorted(connections))
    return formatted_connections

def generate_sequence_diagram(services):
    """Generates a Mermaid sequence diagram from Docker Compose service data."""
    diagram = "sequenceDiagram\n"
    for service_name in services:
        diagram += f"    participant {sanitize_for_mermaid_id(service_name)} as {service_name}<br>{services[service_name]['image']}\n"
    for service_name, details in services.items():
        if 'depends_on' in details:
            for dependency in details['depends_on']:
                diagram += f"    {sanitize_for_mermaid_id(dependency)}->>{sanitize_for_mermaid_id(service_name)}: request/response\n"
    return diagram

def document_docker_compose(compose_file_path, template_path, output_path, append=False):
    compose_data = load_yaml_file(compose_file_path)
    services = {}
    networks = compose_data.get('networks', {})

    for service_name, service_details in compose_data.get('services', {}).items():
        services[service_name] = {
            'ports': parse_ports(service_details),
            'image': service_details.get('image', ''),
            'volumes': service_details.get('volumes', []),
            'environment': normalize_environment(service_details.get('environment', {})),
            'depends_on': service_details.get('depends_on', []),
            'networks': service_details.get('networks', []),
            'command': service_details.get('command', 'No command specified')
        }

    context = {
        'services': services,
        'networks': networks,
        'example_commands': {
            'start': 'docker compose up -d',
            'stop': 'docker compose down',
            'view_logs': 'docker compose logs [service]'
        },
        'troubleshooting': [
            "Ensure Docker is running before starting services.",
            "Check container logs if a service fails to start.",
            "Verify network connections if services can't communicate."
        ],
        'maintenance_tips': [
            "To update a service, modify the image tag and run `docker-compose up -d`.",
            "Review and apply environment variable changes without rebuilding containers."
        ],
        'mermaid_diagram': generate_mermaid_diagram(services, networks),
        'sankey_diagram_network': generate_sankey_diagram_network(services, networks),
        'sankey_diagram_depends': generate_sankey_diagram_depends(services, networks),
        'sequence_diagram': generate_sequence_diagram(services)  # Add sequence diagram to context
    }
    render_template(template_path if template_path else 'dockumentor_compose.md', output_path, context, append)

@click.command()
@click.option('--compose-file', required=True, help='Path to the docker-compose.yml file.')
@click.option('--template', default=None, help='Path to the Jinja2 template file.')
@click.option('--output', default='README.md', help='Path to output the generated documentation.')
@click.option('--append', is_flag=True, help='Append to existing README.md file.')
def cli(compose_file, template, output, append):
    """CLI to generate documentation from a docker-compose file."""
    document_docker_compose(compose_file, template, output, append)

if __name__ == '__main__':
    cli()
