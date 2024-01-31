import os
import sys
import subprocess
import re
import requests
import zipfile
import shutil
import tempfile
import argparse
import platform

def get_system_architecture():
    os_name = platform.system().lower()
    architecture = platform.machine()
    print(f"Detected OS: {os_name}")
    print(f"Detected Architecture: {architecture}")

    if architecture == 'x86_64' or architecture == 'AMD64':
        architecture = 'amd64'
    elif architecture.startswith('arm') or architecture.startswith('aarch64'):
        architecture = 'arm64'  # Use 'arm64' for ARM-based Macs
    else:
        raise ValueError(f"Unsupported architecture: {architecture}")
    return os_name, architecture

def download_terraform(version, os_name, architecture):
    terraform_url = f"https://releases.hashicorp.com/terraform/{version}/terraform_{version}_{os_name}_{architecture}.zip"
    response = requests.get(terraform_url, stream=True)

    if response.status_code == 404:
        sys.exit(f"Error: Terraform version {version} is not available for your OS and architecture.")
    response.raise_for_status()

    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_file:
        shutil.copyfileobj(response.raw, temp_file)
        return temp_file.name

def install_terraform(version, install_dir, zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(install_dir)
    os.chmod(os.path.join(install_dir, 'terraform'), 0o755)

def create_symlink(target, link_path):
    if os.path.exists(link_path) or os.path.islink(link_path):
        os.remove(link_path)
    os.symlink(target, link_path)

def get_tf_bin_path():
    current_platform = platform.system().lower()
    
    if current_platform == 'darwin':
        # macOS (Homebrew)
        tf_path = subprocess.run(['brew', '--prefix', 'terraform'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if tf_path.returncode == 0:
            return os.path.join(tf_path.stdout.strip(), 'bin', 'terraform')
    
    if current_platform == 'linux' and os.geteuid() == 0:
        return os.path.join(os.path.expanduser("~"), ".tfVersions", args.terraform_version, 'terraform')
    
    tf_path = subprocess.run(['which', 'terraform'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if tf_path.returncode == 0:
        return tf_path.stdout.strip()
    
    return "/usr/local/bin/terraform"  # Default path if Terraform is not installed

def list_available_versions():
    response = requests.get("https://releases.hashicorp.com/terraform/")
    if response.status_code == 200:
        page_content = response.text
        versions = re.findall(r'<a href="/terraform/([0-9]+\.[0-9]+\.[0-9]+)/"', page_content)

        installed_version = detect_installed_version()

        for version in versions:
            if version == installed_version:
                print(f"\033[92m* {version}\033[0m")
            else:
                print(f"  {version}")
    else:
        sys.exit(f"Failed to fetch available Terraform versions. Status code: {response.status_code}")

def detect_installed_version():
    tf_path = get_tf_bin_path()

    if tf_path:
        try:
            version_output = subprocess.check_output([tf_path, "-v"], stderr=subprocess.STDOUT).decode()
            match = re.search(r'Terraform v([0-9]+\.[0-9]+\.[0-9]+)', version_output)
            if match:
                return match.group(1)
        except subprocess.CalledProcessError:
            pass
    return None

def get_latest_version():
    response = requests.get("https://releases.hashicorp.com/terraform/")
    if response.status_code == 200:
        page_content = response.text
        versions = re.findall(r'<a href="/terraform/([0-9]+\.[0-9]+\.[0-9]+)/"', page_content)

        # Initialize a variable to store the latest version
        latest_version = None

        # Loop through the versions and find the highest version
        for version in versions:
            if latest_version is None or version > latest_version:
                latest_version = version

        return latest_version

    return None

def install_subcommand(args):
    os_name, architecture = get_system_architecture()
    tf_bin_path = get_tf_bin_path()
    
    if args.terraform_version == "latest":
        args.terraform_version = get_latest_version()  # Get the latest version
        if not args.terraform_version:
            sys.exit("Error: No Terraform version found. Please specify a valid version or use 'list' to see available versions.")
    
    tf_dir_path = os.path.join(os.path.dirname(tf_bin_path), f".tfVersions/{args.terraform_version}")

    if platform.system().lower() == "linux" and "Microsoft" in platform.uname().release:
        # Running on WSL, use the user's home directory as the destination
        tf_dir_path = os.path.join(os.path.expanduser("~"), ".tfVersions", args.terraform_version)

    tf_version_path = os.path.join(tf_dir_path, 'terraform')

    if not os.path.isfile(tf_version_path):
        if not os.path.exists(tf_dir_path):
            os.makedirs(tf_dir_path)

        try:
            temp_zip_path = download_terraform(args.terraform_version, os_name, architecture)
            install_terraform(args.terraform_version, tf_dir_path, temp_zip_path)
            os.remove(temp_zip_path)
        except requests.HTTPError as e:
            sys.exit(f"Failed to download Terraform: {e}")

    create_symlink(tf_version_path, tf_bin_path)

    try:
        version_output = subprocess.check_output([tf_bin_path, "-v"], stderr=subprocess.STDOUT).decode()
        print(version_output.split('\n')[0])
    except subprocess.CalledProcessError as e:
        sys.exit(f"Error in executing Terraform: {e}")

def current_subcommand(args):
    installed_version = detect_installed_version()
    if installed_version:
        print(f"Currently installed Terraform version: {installed_version}")
    else:
        print("Terraform is not currently installed.")

def list_subcommand(args):
    list_available_versions()

def help_subcommand(args):
    print("Terraform Version Manager: A tool for switching between different versions of Terraform. Run `tvm -h` for more information.")
    
def show_version(args):
    import pkg_resources
    version = pkg_resources.get_distribution("terraform-version-manager").version
    print(f"TVM (Terraform Version Manager) version {version}")
    
def main():
    parser = argparse.ArgumentParser(description='Terraform Version Manager: A tool for switching between different versions of Terraform.')
    parser.add_argument('--version', action='store_true', help='Show the version of TVM')

    subparsers = parser.add_subparsers()

    install_parser = subparsers.add_parser('install', help='Install a specific version of Terraform. E.g. `tvm install latest`, `tvm install 1.5.7`')
    install_parser.add_argument('terraform_version', help='Specify the version of Terraform to install.')
    install_parser.set_defaults(func=install_subcommand)

    current_parser = subparsers.add_parser('current', help='Show the currently installed Terraform version.')
    current_parser.set_defaults(func=current_subcommand)

    list_parser = subparsers.add_parser('list', help='List available Terraform versions.')
    list_parser.set_defaults(func=list_subcommand)

    help_parser = subparsers.add_parser('help', help='Show this help message.')
    help_parser.set_defaults(func=help_subcommand)

    args = parser.parse_args()
    if args.version:
        show_version(args)
    elif hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
