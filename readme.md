### Dockumentor: Docker Compose Documentation Generator

**Dockumentor** is a tool designed to automatically generate comprehensive documentation for Docker Compose configurations.

#### Features:
- **Mermaid Diagram Generation:** Automatically generate Mermaid diagrams that visually map the service relationships and network configurations.
- **Sankey Diagrams for Network and Dependency Insights:** Visualize network ports and service dependencies through Sankey diagrams to better understand internal and external bindings and service interactions.
- **Template-based Documentation:** Customize documentation output using Jinja2 templates, allowing for flexibility in how information is presented.
- **CLI Support:** Comes with a command-line interface to easily generate and update documentation directly from the terminal.
- **Configurable:** Easily adaptable to include more detailed information such as volume mappings, environment variables, and custom commands through a simple YAML configuration.

#### Ideal for:
- Developers looking to automate the documentation of their Docker environments.
- Teams requiring consistent and updated documentation for development, testing, and production setups.
- Educators and trainers who provide tutorials or workshops on Docker and need clear, visual representations of complex configurations.

By simplifying the documentation process, **Dockumentor** helps you focus more on development and less on the manual effort of maintaining up-to-date documentation of your Docker setups.

## Installation

To install Dockumentor, you can use pip, the Python package manager. Make sure you have Python and pip installed on your system. Then run the following command:

```bash
pip install dockumentor
```

## Usage

Once installed, you can use the Dockumentor CLI to generate a README for your project with Docker Compose.

### Generating Documentation

To generate a README for a project with a Docker Compose configuration, navigate to your project directory and run the following command:

```bash
dockumentor --compose-file path/to/docker-compose.yml --output README.md
```

- `--compose-file`: Specify the path to your `docker-compose.yml` file.
- `--output`: Specify the path to the output file (e.g., `README.md`). This is where the generated documentation will be written.

### Example Command

```bash
dockumentor --compose-file ./docker-compose.yml --output ./README.md
```

### Appending to Existing Documentation

If you want to append the generated documentation to an existing README file, use the `--append` option:

```bash
dockumentor --compose-file ./docker-compose.yml --output ./README.md --append
```

This will insert the generated documentation within specific markers in the existing README file, ensuring that the new content is added without overwriting the existing content.

### Customizing the Template

Dockumentor uses Jinja2 templates to format the generated documentation. You can customize the template to match your project's documentation style. Create a custom template file and specify its path using the `--template` option.

#### Example Command with Custom Template

```bash
dockumentor --compose-file ./docker-compose.yml --template ./templates/dockumentor_compose.md --output ./README.md
```

This command specifies a custom template for generating the documentation. If you don't specify a template, Dockumentor will use a default template.

## Author

- [Lucian BLETAN](https://github.com/gni)
