import argparse
from utils.logger import log, stream_handler, file_handler
from utils.config import Config
from migrate import Migrate
import sys
import signal
def main():
    parser = argparse.ArgumentParser(description="Migration tool for Kubernetes\nex: python3 main.py -gmpr")
    parser.add_argument("--generate", "-g", help="Generate configuration files", action="store_true")
    parser.add_argument("--config", "-c", help="Path to configuration file", default="config.yaml", action="store")
    parser.add_argument("--verbose", "-v", help="Enable verbose logging", action="store_true")
    parser.add_argument("--display", "-d", help="Display configuration", action="store_true")
    parser.add_argument("--mount", "-m", help="Mount all the directory", action="store_true")
    parser.add_argument("--run", "-r", help="Run the migration", action="store_true")
    parser.add_argument("--dry-run", "-n", help="Perform a dry run", action="store_true")
    parser.add_argument("--unmount", "-u", help="Unmount all the directory", action="store_true")
    parser.add_argument("--mapping", "-p", help="Path to mapping file", action="store_true")
    args = parser.parse_args()

    if args.verbose:
        stream_handler.setLevel("DEBUG")
        log.setLevel("DEBUG")
        log.debug("Verbose logging enabled")
    file_handler.setLevel("DEBUG")
    if args.generate:
        config = Config(args.config, generate=True)
        config.fill()    
    if args.display:
        config = Config(args.config)
        config.display()
    if args.mount or args.run or args.unmount:
        migration = Migrate(Config(args.config), args.dry_run)
    if args.unmount:
        migration.unmount()
    if args.mount:
        migration.mount()
    if args.mapping:
        config = Config(args.config)
        config.mapping()
    if args.run:
        migration.run()
    if not args.generate and not args.display and not args.mount and not args.run and not args.unmount and not args.mapping:
        parser.print_help()

def signal_handler(sig, frame):
    log.warning("Exiting...")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    main()
