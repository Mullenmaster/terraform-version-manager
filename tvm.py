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

def parse_arguments():
    parser = argparse.ArgumentParser(description='Terraform Version Manager: A tool for switching between different versions of Terraform.')
    parser.add_argument('-v', '--version', nargs='?', help='Specify the version of Terraform to use. Example: -v 0.12.19')
    parser.add_argument('-l', '--list', action='store_true', help='List available Terraform versions') 
    return parser.parse_args()


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
    tf_path = shutil.which("terraform")
    if tf_path:
        return tf_path
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
    tf_path = shutil.which("terraform")
    
    if tf_path:
        try:
            version_output = subprocess.check_output([tf_path, "-v"], stderr=subprocess.STDOUT).decode()
            match = re.search(r'Terraform v([0-9]+\.[0-9]+\.[0-9]+)', version_output)
            if match:
                return match.group(1)
        except subprocess.CalledProcessError:
            pass
    return None

def main():
    args = parse_arguments()

    if args.list:
        list_available_versions()
        return

    if args.version:
        tf_version = args.version
    else:
        tf_version = None
        try:
            with open('terraform.lock.hcl', 'r') as lock_file:
                content = lock_file.read()
                match = re.search(r'version\s*=\s*"([0-9]+\.[0-9]+\.[0-9]+)"', content)
                if match:
                    tf_version = match.group(1)
                else:
                    raise ValueError("Terraform version not found in terraform.lock.hcl.")
        except FileNotFoundError:
            sys.exit("Error: No terraform.lock.hcl file found. Please specify a Terraform version using -v.")

    os_name, architecture = get_system_architecture()
    tf_bin_path = get_tf_bin_path()
    tf_dir_path = os.path.join(os.path.dirname(tf_bin_path), f".tfVersions/{tf_version}")
    tf_version_path = os.path.join(tf_dir_path, 'terraform')

    if not os.path.isfile(tf_version_path):
        if not os.path.exists(tf_dir_path):
            os.makedirs(tf_dir_path)

        try:
            temp_zip_path = download_terraform(tf_version, os_name, architecture)
            install_terraform(tf_version, tf_dir_path, temp_zip_path)
            os.remove(temp_zip_path)
        except requests.HTTPError as e:
            sys.exit(f"Failed to download Terraform: {e}")

    create_symlink(tf_version_path, tf_bin_path)

    try:
        version_output = subprocess.check_output([tf_bin_path, "-v"], stderr=subprocess.STDOUT).decode()
        print(version_output.split('\n')[0])
    except subprocess.CalledProcessError as e:
        sys.exit(f"Error in executing Terraform: {e}")

if __name__ == "__main__":
    main()
