import sys
import lib.vpn_manager as vpn_manager


def main():
    try:
        # Create instances from NordVPN class.
        vpn_driver = vpn_manager.NordVPN()

        # Connect to the NordVPN server.
        vpn_driver.connect()

        # Check the information on the server you connected.
        print(vpn_driver.nordvpn_info)

    except Exception as e:
        print(e)

    finally:
        # Disconnect from the NordVPN server.
        if 'vpn_driver' in locals():
            vpn_driver.disconnect()


if __name__ == "__main__":
    sys.exit(main())
