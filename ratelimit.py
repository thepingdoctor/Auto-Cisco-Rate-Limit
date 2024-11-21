import os
import time
import logging
from netmiko import ConnectHandler

# Configure logging
logging.basicConfig(
    filename='rate_limit_changes.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

# Switch connection details using environment variables
switch = {
    'device_type': 'cisco_ios',
    'host': os.getenv('SWITCH_IP'),                  # Set the environment variable SWITCH_IP
    'username': os.getenv('SWITCH_USERNAME'),         # Set the environment variable SWITCH_USERNAME
    'password': os.getenv('SWITCH_PASSWORD'),         # Set the environment variable SWITCH_PASSWORD
    'secret': os.getenv('SWITCH_ENABLE_PASSWORD'),    # Set the environment variable SWITCH_ENABLE_PASSWORD
    'port': 22,                                       # Default SSH port
}

# Adjusted rate limits in bits per second (bps)
rate_limits = [

    2944000,    # Adjusted from 2,938,033 bps to 2,944,000 bps (2.944 Mbps)
    14400000,   # Adjusted from 14,389,400 bps to 14,400,000 bps (14.4 Mbps)
    9312000,    # Adjusted from 9,313,231 bps to 9,312,000 bps (9.312 Mbps)
    22400000,   # Adjusted from 22,424,200 bps to 22,400,000 bps (22.4 Mbps)
    7424000,    # Adjusted from 7,423,800 bps to 7,424,000 bps (7.424 Mbps)
    17344000,   # Adjusted from 17,332,300 bps to 17,344,000 bps (17.344 Mbps)
    6944000,    # Adjusted from 6,938,033 bps to 6,944,000 bps (6.944 Mbps)
    27456000,   # Adjusted from 27,442,900 bps to 27,456,000 bps (27.456 Mbps)
    9952000,    # Adjusted from 9,938,033 bps to 9,952,000 bps (9.952 Mbps)
    15360000,   # Adjusted from 15,324,300 bps to 15,360,000 bps (15.36 Mbps)
    34304000,   # Adjusted from 34,313,410 bps to 34,304,000 bps (34.304 Mbps)
    18336000    # Adjusted from 18,324,300 bps to 18,336,000 bps (18.336 Mbps)
]

# Create an iterator to cycle through rate limits
rate_limits_cycle = iter(rate_limits)

def change_rate_limit(rate_limit):
    try:
        # Connect to the switch
        net_connect = ConnectHandler(**switch)
        # Enter enable mode
        net_connect.enable()

        # Configuration commands
        config_commands = [
            'policy-map tkm-soft',
            'class limit50',
            'no police',
            f'police cir {rate_limit}',
            '  conform-action transmit',
            '  exceed-action drop',
            'end',
            'write memory'
        ]

        # Send configuration commands
        output = net_connect.send_config_set(config_commands)
        logging.info(f"Rate limit changed to {rate_limit} bps")
        print(output)

        # Disconnect from the switch
        net_connect.disconnect()
        print(f"Rate limit changed to {rate_limit} bps")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    # Check if all environment variables are set
    required_env_vars = ['SWITCH_IP', 'SWITCH_USERNAME', 'SWITCH_PASSWORD', 'SWITCH_ENABLE_PASSWORD']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        print(f"Error: The following environment variables are not set: {', '.join(missing_vars)}")
        exit(1)

    # Main loop to change the rate limit every 15 minutes
    while True:
        try:
            # Get the next rate limit from the cycle
            rate_limit = next(rate_limits_cycle)
        except StopIteration:
            # Restart the cycle if we've reached the end
            rate_limits_cycle = iter(rate_limits)
            rate_limit = next(rate_limits_cycle)

        # Change the rate limit on the switch
        change_rate_limit(rate_limit)

        # Wait for 15 minutes (900 seconds)
        time.sleep(900)