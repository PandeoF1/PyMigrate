import yaml
from utils.logger import log
import datetime
from pprint import pprint
import inquirer
from rich.console import Console
from rich.table import Table
from rich import box
import os


class Config:
    """
    This class is responsible for loading and generating configuration files.
    """

    def __init__(self, path='config.yaml', generate=False):
        self.path = path
        if generate:
            self.config = self.generate_config()
        else:
            self.config = self.load_config()

    """
    This method loads the configuration file from the path specified in the constructor.
    If the file is not found, it will generate a default configuration file.
    """

    def load_config(self):
        log.debug(f"Loading configuration file from {self.path}")
        try:
            with open(self.path, 'r') as f:
                config_data = yaml.safe_load(f)  # Load the YAML data
                log.debug(f"Configuration file loaded: {self.path}")
                return config_data  # Return the loaded config
        except FileNotFoundError:
            log.error(f"Configuration file not found: {self.path}")
            exit(1)

    """
    This method generates a default configuration file at the path specified in the constructor.
    """

    def generate_config(self):
        log.debug("Generating configuration file...")
        try:
            with open(self.path, 'w') as f:
                f.write(yaml.dump(self.template))
            log.debug(f"Configuration file generated at {self.path}")
            return self.template
        except Exception as e:
            log.error(f"Failed to generate configuration file: {e}")
            exit(1)
    """
    This method updates the configuration file with the current configuration.
    """

    def update_config(self):
        log.debug("Updating configuration file...")
        try:
            with open(self.path, 'w') as f:
                f.write(yaml.dump(self.config))
            log.debug(f"Configuration file updated at {self.path}")
        except Exception as e:
            log.error(f"Failed to update configuration file: {e}")
            exit(1)

    """
    This method will ask for hosts debugrmations (hostname, ip, user, port)
    """

    def ask_hosts(self):
        hosts = []
        while True:
            host = {"hostname": inquirer.prompt([inquirer.Text(
                'hostname', default="localhost", message="Enter hostname for the new host")])['hostname']}
            hosts.append({
                "hostname": host['hostname'],
                "ip": inquirer.prompt([inquirer.Text('ip', default="x.x.x.x", message=f"Enter IP address for {host['hostname']}")])['ip'],
                "user": inquirer.prompt([inquirer.Text('user', default="root", message=f"Enter user for {host['hostname']}")])['user'],
                "port": inquirer.prompt([inquirer.Text('port', default="22", message=f"Enter port for {host['hostname']}")])['port'],
                "mountPath": inquirer.prompt([inquirer.Text('mountPath', default="/opt/docker", message=f"Enter mount point for {host['hostname']}")])['mountPath'],
            })
            if inquirer.prompt([inquirer.List('add', message="Add another host?", choices=["yes", "no"])])['add'] == "no":
                break
        return hosts

    """
    This method returns the available sources.
    """

    def available_sources(self):
        return ["nfs", "local", "sshfs"]

    """
    This method returns the configuration for the source.
    """

    def config_sources(self, source):
        if source == "nfs":
            return {
                "type": "nfs",
                "server": inquirer.prompt([inquirer.Text('server', default="x.x.x.x", message="Enter NFS source server")])['server'],
                "serverPath": inquirer.prompt([inquirer.Text('serverPath', default="/srv/nfs/", message="Enter NFS server path")])['serverPath'],
                "mountPath": inquirer.prompt([inquirer.Text('mountPath', default="/migration/source", message="Enter NFS mount path")])['mountPath'],
            }
        elif source == "local":
            return {
                "type": "local",
                "mountPath": inquirer.prompt([inquirer.Text('mountPath', default="/migration/source", message="Enter local source path")])['mountPath'],
            }
        elif source == "sshfs":
            return {
                "type": "sshfs",
                "options": inquirer.prompt([inquirer.Text('options', default="allow_other,allow_root,noauto_cache,reconnect", message="Enter SSHFS options")])['options'],
                "hosts": self.ask_hosts(),
                "mountPath": inquirer.prompt([inquirer.Text('mountPath', default="/migration/source", message="Enter SSHFS mount path ($path + /$node)")])['mountPath'],
            }
        else:
            log.error("Invalid source type")
            exit(1)

    """
    This method returns the available destinations.
    """

    def available_destinations(self):
        return ["local"]

    """
    This method returns the configuration for the destination.
    """

    def config_destinations(self, destination):
        if destination == "local":
            return {
                "type": "local",
                "mountPath": inquirer.prompt([inquirer.Text('mountPath', default="/migration/dest", message="Enter local source path")])['mountPath'],
            }
        else:
            log.error("Invalid destination type")
            exit(1)

    """
    This method returns the available copy options.
    """

    def available_tools(self):
        return ["rsync"]

    """
    This method returns the configuration for the copy options.
    """

    def config_tools(self, copy_option):
        if copy_option == "rsync":
            return {
                "type": "rsync",
                "options": inquirer.prompt([inquirer.Text('options', default="-aKhz", message="Enter rsync options")])['options']
            }
        else:
            log.error("Invalid copy option")
            exit(1)

    """
    This method asks the user to fill the configuration file
    """

    def fill(self):
        # Ask for source type
        log.debug(f"Available sources: {self.available_sources()}")
        source = inquirer.prompt([inquirer.List(
            'source', message="Select source type", choices=self.available_sources())])['source']
        self.config["source"] = self.config_sources(source)
        # Ask for destination type
        log.debug(f"Available destinations: {self.available_destinations()}")
        destination = inquirer.prompt([inquirer.List(
            'destination', message="Select destination type", choices=self.available_destinations())])['destination']
        self.config["destination"] = self.config_destinations(destination)

        # Ask for copy options
        log.debug(f"Available copy options: {self.available_tools()}")
        tools = inquirer.prompt([inquirer.List(
            'tools', message="Select copy tools", choices=self.available_tools())])['tools']
        self.config["tools"] = self.config_tools(tools)

        # Ask for SSH options if both are not local
        if self.config["source"]["type"] == "sshfs" or self.config["destination"]["type"] == "sshfs":
            log.debug("SSH options should be provided")
            # ask if user wants to provide SSH options
            self.config["ssh"] = {
                "pub": inquirer.prompt([inquirer.Text('pub', default="~/.ssh/id_rsa.pub", message="Enter SSH key path")])['pub'],
                "priv": inquirer.prompt([inquirer.Text('priv', default="~/.ssh/id_rsa", message="Enter SSH key path")])['priv'],
            }

        # Update the configuration file
        self.update_config()

    """
    This method displays the configuration file
    """

    def display(self):
        log.debug("Displaying configuration file...")

        # Create a rich Console object
        console = Console()

        # Create a table for source configuration
        source_table = Table(title="Source Configuration",
                             box=box.ROUNDED, show_lines=True)
        source_table.add_column("Key", justify="center", style="cyan")
        source_table.add_column("Value", justify="center", style="green")

        # Fill the table with source config data
        for key, value in self.config.get("source", {}).items():
            source_table.add_row(key, str(value))

        # Create a table for destination configuration
        destination_table = Table(
            title="Destination Configuration", box=box.ROUNDED, show_lines=True)
        destination_table.add_column("Key", justify="center", style="cyan")
        destination_table.add_column("Value", justify="center", style="green")

        # Fill the table with destination config data
        for key, value in self.config.get("destination", {}).items():
            destination_table.add_row(key, str(value))

        # Create a table for tools configuration
        tools_table = Table(title="Tools Configuration",
                            box=box.ROUNDED, show_lines=True)
        tools_table.add_column("Key", justify="center", style="cyan")
        tools_table.add_column("Value", justify="center", style="green")

        # Fill the table with tools config data
        for key, value in self.config.get("tools", {}).items():
            tools_table.add_row(key, str(value))

        # Optionally, create a table for SSH configuration if present
        if "ssh" in self.config:
            ssh_table = Table(title="SSH Configuration",
                              box=box.ROUNDED, show_lines=True)
            ssh_table.add_column("Key", justify="center", style="cyan")
            ssh_table.add_column("Value", justify="center", style="green")
            for key, value in self.config.get("ssh", {}).items():
                ssh_table.add_row(key, str(value))
            # Display SSH config table
            console.print(ssh_table)

        # Display all the tables
        console.print(source_table)
        console.print(destination_table)
        console.print(tools_table)

    """
    Check if the configuration is valid
    """

    def validate(self):
        log.debug("Validating configuration...")
        if "source" not in self.config:
            log.error("Source configuration is missing")
            if self.config["source"] not in self.available_sources():
                log.error("Invalid source")
            exit(1)
        if "destination" not in self.config:
            log.error("Destination configuration is missing")
            if self.config["destination"] not in self.available_destinations():
                log.error("Invalid destination")
            exit(1)
        if "tools" not in self.config:
            log.error("Tools configuration is missing")
            if self.config["tools"] not in self.available_tools():
                log.error("Invalid copy tool")
            exit(1)
        if self.config["source"]["type"] == "sshfs" or self.config["destination"]["type"] == "sshfs":
            if "ssh" not in self.config:
                log.error("SSH configuration is missing")
                exit(1)
        log.debug("Configuration is valid")

    """
    Return the configuration in plain dictionary format
    """

    def plain(self):
        return self.config

    """
    This method will ask the user to map the PVCs
    """

    def mapping_pvc(self, source_dir, dest_dir, type):
        log.info(
            """Execute: `kubectl -n <namespace> get pvc -o jsonpath='{range .items[*]}{"- Name: "}{.metadata.name}{"\\n  VolumeName: "}{.spec.volumeName}{"\\n"}{end}'` on the source cluster to get the PVC UUID->Name mapping""")
        _pvc_file = inquirer.prompt([inquirer.Text(
            'pvc_file', default="pvc.yaml", message="Enter PVC file name")])['pvc_file']
        # Check provided file
        try:
            with open(_pvc_file, 'r') as f:
                pvc_data = yaml.safe_load(f)
                for pvc in pvc_data:
                    # Check if the PVC is in the source directory
                    log.debug(
                        f"Checking if source directory exists for {os.path.join(source_dir, pvc[type])}")
                    if not os.path.isdir(f"{source_dir}/{pvc[type]}"):
                        log.error(
                            f"Source directory not found for {pvc['Name']}")
                        exit(1)
        except FileNotFoundError:
            log.error(f"File not found: {_pvc_file}")
            exit(1)
        except Exception as e:
            log.error(f"An unexpected error occurred: {e}")
            exit(1)

        # Check if the destination of each PVC is in the destination directory
        mapping = []
        for pvc in pvc_data:
            # Check if the PVC is in the source directory
            log.debug(
                f"Checking if destination directory exists for {os.path.join(dest_dir, pvc['Name'])}")
            if os.path.isdir(f"{dest_dir}/{pvc['Name']}"):
                log.debug(f"Mapping {pvc[type]} to {pvc['Name']}")
                if inquirer.prompt([inquirer.List('confirm', message=f"Confirm mapping for {source_dir}/{pvc[type]} ({pvc['Name']}) to {dest_dir}/{pvc['Name']}", choices=["yes", "no"])])['confirm'] == "yes":
                    subpath = inquirer.prompt([inquirer.Checkbox(
                        'subpath', message=f"Select if subpath is activated ({pvc['Name']})", choices=["from", "to"])])['subpath']
                    mapping.append(
                        {
                            pvc['Name']: {
                                "from": f"{source_dir}/{pvc[type]}" + ("/data" if "from" in subpath else ""),
                                "to": f"{dest_dir}/{pvc['Name']}" + ("/data" if "to" in subpath else ""),
                            }
                        }
                    )
            else:
                log.warning(
                    f"Destination directory not found for {pvc['Name']}")
                _input = inquirer.prompt([inquirer.Text(
                    'confirm', message=f"Enter destination directory for {source_dir}/{pvc[type]} ({pvc['Name']}) (Empty to skip)")])['confirm']
                if _input:
                    if os.path.isdir(_input):
                        subpath = inquirer.prompt([inquirer.Checkbox(
                            'subpath', message=f"Select if subpath is activated ({pvc['Name']})", choices=["from", "to"])])['subpath']
                        mapping.append(
                            {
                                pvc['Name']: {
                                    "from": f"{source_dir}/{pvc[[type]]}" + ("/data" if "from" in subpath else ""),
                                    "to": _input + ("/data" if "to" in subpath else ""),
                                }

                            }
                        )
                    else:
                        log.error(f"Destination directory not found: {_input}")
                        exit(1)
        self.update_mapping(mapping)

    """
    This method will ask the user to map the source and destination directories 
    """

    def mapping_custom(self):
        # ask for each entry (source -> destination)
        mapping = []
        while True:
            _input = inquirer.prompt([inquirer.Text(
                'mapping', message="Enter source -> destination mapping (Empty to stop)")])['mapping']
            if _input:
                _input = _input.split("->")
                if len(_input) == 2:
                    mapping.append(
                        {
                            "from": _input[0].strip(),
                            "to": _input[1].strip()
                        }
                    )
                else:
                    log.error("Invalid mapping")
            else:
                break
        self.update_mapping(mapping)

    """
    This method will update the mapping in the configuration file
    """

    def update_mapping(self, mapping):
        self.config["mapping"] = mapping
        self.update_config()

    """
    Mapping the source and destination directories
    """

    def mapping(self):
        log.debug("Mapping the source and destination directories")
        # Get the source and destination directories
        source_dir = os.path.realpath(self.config["source"]["mountPath"])
        dest_dir = os.path.realpath(self.config["destination"]["mountPath"])
        # Display the mapping
        log.info(
            f"Mapping source directory: {source_dir} to destination directory: {dest_dir}")

        # Ask if the mapping is baded on pvc, docker volume or custom
        _mapping = inquirer.prompt([inquirer.List('mapping', message="Select mapping type", choices=[
                                   "pvc uuid", "pvc name", "docker volume", "custom"])])['mapping']
        self.update_mapping([])
        if _mapping == "pvc uuid":
            self.mapping_pvc(source_dir, dest_dir, "VolumeName")
        elif _mapping == "pvc name":
            self.mapping_pvc(source_dir, dest_dir, "Name")
        elif _mapping == "custom":
            self.mapping_custom()
        pass

    template = {
        "_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": {},
        "destination": {},
        "tools": {}
    }
