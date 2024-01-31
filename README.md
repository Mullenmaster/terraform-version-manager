# Terraform Version Manager (TVM) - Command Line Tool

Terraform Version Manager (TVM) is a command-line tool that allows you to easily switch between different versions of Terraform, the infrastructure as code (IaC) tool developed by HashiCorp. With TVM, you can install, manage, and use multiple versions of Terraform on your system.

## Table of Contents

- [Terraform Version Manager (TVM) - Command Line Tool](#terraform-version-manager-tvm---command-line-tool)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
    - [Permissions on WSL2](#permissions-on-wsl2)
  - [Usage](#usage)
    - [Install a Specific Version](#install-a-specific-version)
    - [Check Currently Installed Version](#check-currently-installed-version)
    - [List Available Terraform Versions](#list-available-terraform-versions)
  - [Contributing](#contributing)
  - [License](#license)

## Installation

To install Terraform Version Manager (TVM), follow these steps:

1. Clone, install, and verify tvm on your local machine by running:

```bash
git clone https://github.com/mullenmaster/terraform-version-manager
cd terraform-version-manager
pip install .

# verify the install
tvm --version
```

### Permissions on WSL2

You may need to open up access to your install directory:

```bash
sudo chown -R your_username:your_username /path/to/installation/directory
sudo chmod -R u+w /path/to/installation/directory
```

## Usage

TVM provides a set of commands to manage Terraform versions. Here are the available commands and their usage:

### Install a Specific Version

To install a specific version of Terraform, use the `install` command followed by the desired version number. For example, to install Terraform version 1.5.7, run:

```bash
tvm install 1.5.7
```

You can also use the `latest` keyword to install the latest available version of Terraform:

```bash
tvm install latest
```

If the specified version or `latest` is not available for your operating system and architecture, TVM will display an error message.

### Check Currently Installed Version

To check the currently installed version of Terraform, use the `current` command:

```bash
tvm current
```

This command will display the currently installed Terraform version.

### List Available Terraform Versions

To list all available Terraform versions that you can install, use the `list` command:

```bash
tvm list
```

The command will fetch and display a list of available Terraform versions. The currently installed version, if any, will be highlighted with an asterisk (\*) in front of it.

## Contributing

Contributions to Terraform Version Manager (TVM) are welcome! If you find any issues, have ideas for improvements, or want to contribute code, please check out the [contribution guidelines](CONTRIBUTING.md).

## License

Terraform Version Manager (TVM) is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
