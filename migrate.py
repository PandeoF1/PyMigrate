from utils.config import Config
from utils.logger import log
import os
import subprocess
import re
from rich.progress import Progress


def is_mounted(mount_path):
    """Check if the given mount path is currently mounted."""
    mount_path = os.path.realpath(mount_path)
    with open('/proc/mounts', 'r') as f:
        mounts = f.read()
    log.debug(f"Checking if {mount_path} is mounted ({mount_path in mounts})")
    return mount_path in mounts


class Migrate:
    def __init__(self, config: Config, dry_run: bool = False):
        self._config = config
        self.dry_run = dry_run

        self._config.validate()
        self.config = self._config.plain()

    """
    Mount the source directory via NFS
    """

    def mount_nfs(self, config):
        log.debug("Mounting source directory via NFS")

        # Extract NFS server details from the config
        server = config["server"]
        server_path = config["serverPath"]
        mount_path = config["mountPath"]

        # NFS mount command construction
        nfs_mount_cmd = [
            "mount",
            "-t", "nfs",  # Specify NFS as the file system type
            # Server and path in format server:/path
            f"{server}:{server_path}",
            mount_path  # Local mount point
        ]

        # Log the command for debugging
        log.info(f"Executing NFS mount command: {' '.join(nfs_mount_cmd)}")

        # Execute the NFS mount command
        try:
            subprocess.run(nfs_mount_cmd, check=True)
            log.info(
                f"Successfully mounted NFS {server}:{server_path} to {mount_path}")
        except subprocess.CalledProcessError as e:
            log.error(
                f"Failed to mount NFS {server}:{server_path} to {mount_path}: {e}")
            exit(1)
        except Exception as e:
            log.error(
                f"An unexpected error occurred while mounting NFS {server}:{server_path}: {e}")
            exit(1)

    """
    Mount the source directory locally
    """

    def mount_local(self, config):
        log.debug(
            f"Skipping mounting source directory locally {config['mountPath']}")
        pass

    """
    Mount the source directory via SSHFS
    """

    def mount_sshfs(self, config):
        log.debug("Mounting source directory via SSHFS")
        for host in config["hosts"]:
            remote_path = f"{host['user']}@{host['ip']}:{host['mountPath']}"
            mount_path = config['mountPath']
            # Get options, default to empty string if not present
            sshfs_options = config.get('options', '')
            # Use default SSH port 22 if not specified
            port = host.get('port', '22')

            # SSHFS command construction
            sshfs_cmd = [
                "sshfs",
                f"-oPort={port}",  # Add port option
                f"-o{sshfs_options}",     # Additional SSHFS options
                remote_path,       # Remote directory (user@ip:/path)
                mount_path         # Local mount point
            ]

            # Log the command for debugging
            log.info(f"Executing SSHFS command: {' '.join(sshfs_cmd)}")

            # Execute the SSHFS command
            try:
                subprocess.run(sshfs_cmd, check=True)
                log.info(f"Successfully mounted {remote_path} to {mount_path}")
            except subprocess.CalledProcessError as e:
                log.error(
                    f"Failed to mount {remote_path} to {mount_path}: {e}")
                exit(1)
            except Exception as e:
                log.error(
                    f"An unexpected error occurred while mounting {remote_path}: {e}")
                exit(1)

    mount_index = {
        "nfs": lambda self, config: self.mount_nfs(config),
        "local": lambda self, config: self.mount_local(config),
        "sshfs": lambda self, config: self.mount_sshfs(config)
    }

    """
    Unmount the source directory via NFS
    """

    def unmount_nfs(self, config):
        log.debug("Unmounting source directory via NFS")
        mount_path = config["mountPath"]

        # Check if the directory is mounted
        if not is_mounted(mount_path):
            log.info(f"{mount_path} is not mounted. Skipping unmount.")
            return

        # NFS unmount command construction
        nfs_unmount_cmd = [
            "umount",
            mount_path  # Local mount point
        ]

        # Log the command for debugging
        log.info(f"Executing NFS unmount command: {' '.join(nfs_unmount_cmd)}")

        # Execute the NFS unmount command
        try:
            subprocess.run(nfs_unmount_cmd, check=True)
            log.info(f"Successfully unmounted {mount_path}")
        except subprocess.CalledProcessError as e:
            log.error(f"Failed to unmount {mount_path}: {e}")
            exit(1)
        except Exception as e:
            log.error(
                f"An unexpected error occurred while unmounting {mount_path}: {e}")
            exit(1)

    """
    Unmount the source directory locally
    """

    def unmount_local(self, config):
        log.debug(
            f"Skipping unmounting source directory locally {config['mountPath']}")
        pass

    """
    Unmount the source directory via SSHFS
    """

    def unmount_sshfs(self, config):
        log.debug("Unmounting source directory via SSHFS")
        mount_path = config["mountPath"]

        # Check if the directory is mounted
        if not is_mounted(mount_path):
            log.info(f"{mount_path} is not mounted. Skipping unmount.")
            return

        # SSHFS unmount command construction
        sshfs_unmount_cmd = [
            "fusermount",
            "-u",  # Unmount
            mount_path  # Local mount point
        ]

        # Log the command for debugging
        log.info(
            f"Executing SSHFS unmount command: {' '.join(sshfs_unmount_cmd)}")

        # Execute the SSHFS unmount command
        try:
            subprocess.run(sshfs_unmount_cmd, check=True)
            log.info(f"Successfully unmounted {mount_path}")
        except subprocess.CalledProcessError as e:
            log.error(f"Failed to unmount {mount_path}: {e}")
            exit(1)
        except Exception as e:
            log.error(
                f"An unexpected error occurred while unmounting {mount_path}: {e}")
            exit(1)

    unmount_index = {
        "nfs": lambda self, config: self.unmount_nfs(config),
        "local": lambda self, config: self.unmount_local(config),
        "sshfs": lambda self, config: self.unmount_sshfs(config)
    }

    """
    Unmount the source directory via NFS
    """

    def unmount(self):
        log.debug("Unmounting directories")
        log.debug("Source:")
        self.unmount_index[self.config["source"]["type"]](
            self, self.config["source"])
        log.debug("Destination:")
        self.unmount_index[self.config["destination"]["type"]](
            self, self.config["destination"])
        pass

    """
    Mount the source and destination directories
    """

    def mount(self):
        log.debug("Mounting directories")
        log.debug("Source:")
        self.mount_index[self.config["source"]["type"]](
            self, self.config["source"])
        log.debug("Destination:")
        self.mount_index[self.config["destination"]["type"]](
            self, self.config["destination"])
        pass

    def migrate_rsync(self, source, destination, name):
        log.debug(f"Copying {source} to {destination}")

        # Prepare the rsync command
        rsync_cmd = [
            "rsync",
            self.config['tools']['options'],
            "--progress",
            source,
            destination
        ]

        log.debug(f"Executing rsync command: {' '.join(rsync_cmd)}")

        if self.dry_run:
            log.warning(f"Would copy {source} to {destination} ({rsync_cmd})")
            return

        try:
            with Progress() as progress:
                task = progress.add_task(
                    f"[cyan]Migration {name} in progress...", total=100)

                # Run the rsync process and capture output
                process = subprocess.Popen(
                    rsync_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

                current_file = None  # To track the current file being transferred

                for line in process.stdout:
                    # log.debug(line.strip())  # Log each line from rsync

                    # Check if the line contains a filename (rsync lists the filename without a percentage sign)
                    if re.match(r'^[^%]+$', line.strip()) and not line.strip().startswith("sending incremental file list"):
                        current_file = line.strip()  # Assume this is the current file name
                        current_file = os.path.basename(current_file)
                        log.debug(f"[{name}] Current file: {current_file}")

                    # Match the progress percentage for each file in rsync's output
                    match = re.search(r'(\d+)%', line)
                    if match:
                        percent_complete = int(match.group(1))

                        # Update the progress bar with the current file and progress
                        progress.update(
                            task, description=f"[cyan]Migration {name} - {current_file}", completed=percent_complete)

                process.wait()  # Wait for the process to complete

                if process.returncode == 0:
                    progress.update(task, completed=100)
                    log.debug(
                        f"[{name}] Successfully copied {source} to {destination}")
                else:
                    log.error(
                        f"[{name}] Rsync failed with return code {process.returncode} {process.stderr.read()}")
                    exit(1)

        except subprocess.CalledProcessError as e:
            log.error(f"Failed to copy {source} to {destination}: {e}")
            exit(1)
        except Exception as e:
            log.error(
                f"An unexpected error occurred while copying {source} to {destination}: {e}")
            exit(1)

        except subprocess.CalledProcessError as e:
            log.error(f"Failed to copy {source} to {destination}: {e}")
            exit(1)
        except Exception as e:
            log.error(
                f"An unexpected error occurred while copying {source} to {destination}: {e}")
            exit(1)

    """
    Perform a migration
    """

    def run(self):
        log.debug("Running migration")
        if self.dry_run:
            log.info("Performing dry run")
        if not "mapping" in self.config:
            log.error(
                "No mapping found in configuration please use --mapping option to provide mapping")
            exit(1)

        for migrate in self.config['mapping']:
            # This crash sometime
            source = migrate['from'] + ("/" if not migrate['from'].endswith("/") else "")
            destination = migrate['to'] + ("/" if not migrate['to'].endswith("/") else "")
            tools = self.config['tools']
            if tools['type'] == 'rsync':
                self.migrate_rsync(source, destination, migrate['from'])
            else:
                log.error(f"Unsupported tool {tools['type']}")
                exit(1)
        pass
