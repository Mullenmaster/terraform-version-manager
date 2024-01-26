# Terraform Version Manager (TVM)

Terraform Version Manager (TVM) is a Python tool for easily switching between different versions of Terraform. This tool simplifies the process of managing and using different Terraform versions on your system and is cross-platform compatible.

## Installation

### Prerequisites

Before using TVM, make sure you have the following prerequisites installed:

- Python 3.x
- pip (Python package manager)
- Homebrew (Only required for macOS)

### Installation Steps

```bash
git clone https://github.com/mullenmaster/terraform-version-manager
cd terraform-version-manager
pip install .
```

## Usage

TVM provides a command-line interface to manage Terraform versions. Here are some common usage examples:

### Specify a Terraform Version

To specify a particular Terraform version to use, you can pass the `-v` or `--version` option followed by the desired version number. For example:

```bash
tvm -v 0.12.19
```

This command will download and set up Terraform version 0.12.19.

### Automatically Detect and Use Terraform Version

If you don't specify a version, TVM will attempt to detect the version based on your project's `terraform.lock.hcl` file. If the file is found and contains a version specification, TVM will use that version.

```bash
tvm
```

### Listing Available Terraform Versions

You can list all available Terraform versions and see the current version using the following command:

```bash
tvm -l
```

### Uninstalling TVM

To uninstall TVM, you can use pip:

```bash
pip uninstall terraform-version-manager
```

## Contributing

Contributions to TVM are welcome! If you find issues or have ideas for improvements, please open an issue or submit a pull request on the [GitHub repository](https://github.com/mullenmaster/terraform-version-manager).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
