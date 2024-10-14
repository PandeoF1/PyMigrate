# PyMigrate
  Python migration tools


## Table of Contents
<ol>
  <li>
    <a href="#about-the-project">About The Project</a>
  </li>
  <li><a href="#installation">Installation</a></li>
  <li><a href="#usage">Usage</a></li>
  <li><a href="#contributing">Contributing</a></li>
  <li><a href="#maintainers">Maintainers</a></li>
</ol>


## About The Project

This project is a simple script to perform migration between two environments. It can perform a migration from sshfs, nfs, local to local.


## Installation

1. Clone the repo
   ```sh
   git clone https://github.com/PandeoF1/PyMigrate.git
   ```
2. Create a VENV
   ```sh
   python3 -v venv venv && source venv/bin/activate
   ```
3. Install python3 packages
   ```sh
   pip install -r requirements.txt
   ```
<!-- USAGE EXAMPLES -->
## Usage

1. Generate the configuration file
   ```sh
   python3 main.py --generate 
   ```
2. Mount all the volumes
   ```sh
   python3 main.py --mount
   ```
3. Map the sources to the destination
   ```sh
   python3 main.py --mapping
   ```
4. Perform the migration in dry-run mode
   ```sh
   python main.py --run --dry-run
   ```
5. Perform the migration
   ```sh
   python3 main.py --run
   ```

Or in one command
   ```sh
   python3 main.py -gmpr
   ```

<!-- CONTRIBUTING -->
## Contributing

1. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
2. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
3. Push to the Branch (`git push origin feature/AmazingFeature`)
4. Open a Pull Request


## Maintainers

Nard ThÃ©o - theo.nard18@gmail.com
