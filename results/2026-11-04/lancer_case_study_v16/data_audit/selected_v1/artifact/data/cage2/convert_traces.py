#!/usr/bin/env python3
"""
Convert CybORG YAML traces to BabyCyborg format for RPNI learning.

Preprocessing steps:
1. Map CIDR subnet identifiers to semantic names (User, Enterprise, Operational)
2. Translate IP addresses to hostnames via reverse lookup
3. Extract exploit_class for Red actions to resolve non-determinism
4. Properly capture Blue action success/failure from prev_action_status

Usage:
    python convert_traces.py <source_dir> <output_dir> [--max-traces N]

Example:
    python convert_traces.py NewTraces-20260127-1030 cage2_converted --max-traces 5000
"""

import yaml
import os
import glob
import argparse
from pathlib import Path
from collections import defaultdict
from multiprocessing import Pool, cpu_count


def get_subnet_name_from_hostname(hostname):
    """Infer subnet name from hostname.

    Handles two formats:
    1. Generic: Subnet_0_Host_1 -> Subnet_0
    2. Cage2: User0 -> User, Enterprise1 -> Enterprise, Op_Host0 -> Operational
    """
    parts = hostname.split('_')
    if len(parts) >= 2 and parts[0] == 'Subnet':
        return f"{parts[0]}_{parts[1]}"

    if hostname.startswith('User'):
        return 'User'
    elif hostname.startswith('Enterprise') or hostname == 'Defender':
        return 'Enterprise'
    elif hostname.startswith('Op_'):
        return 'Operational'

    return None


def extract_subnet_mapping(trace_data):
    """Extract subnet CIDR -> subnet name mapping from Blue observations."""
    subnet_mapping = {}
    hostname_to_ip = {}
    ip_to_hostname = {}

    blue_obs = trace_data[0]['Blue']['obs']

    for hostname, host_info in blue_obs.items():
        if 'Interface' in host_info and host_info['Interface']:
            interface = host_info['Interface'][0]
            ip_addr = interface.get('IP Address')
            subnet_cidr = interface.get('Subnet')

            if ip_addr:
                hostname_to_ip[hostname] = ip_addr
                ip_to_hostname[ip_addr] = hostname

            if subnet_cidr:
                subnet_name = get_subnet_name_from_hostname(hostname)
                if subnet_name:
                    prefix = subnet_cidr.split('/')[1]
                    subnet_mapping[subnet_cidr] = {'name': subnet_name, 'prefix': prefix}

    return subnet_mapping, hostname_to_ip, ip_to_hostname


def get_subnet_info(subnet_cidr, subnet_mapping):
    """Get subnet name and prefix from CIDR."""
    if subnet_cidr in subnet_mapping:
        info = subnet_mapping[subnet_cidr]
        return info['name'], info['prefix']
    parts = subnet_cidr.split('/')
    return subnet_cidr.split('/')[0], parts[1] if len(parts) > 1 else '28'


def convert_prev_action_status(status):
    """Convert prev_action_status to success string.

    From CybORG/CybORG/Shared/Enums.py:
        1 = Success
        2 = Unknown
        3 = Failure
    """
    if status == 3:  # FAILURE
        return 'FALSE'
    elif status == 2:  # UNKNOWN
        return 'TRUE'
    else:  # 1 = SUCCESS
        return 'TRUE'


def convert_trace(yaml_path, episode_num=1):
    """Convert a single CybORG trace YAML to BabyCyborg format."""
    try:
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"  YAML error in {yaml_path}: {e}")
        return None

    if not data or len(data) < 2:
        print(f"  Empty or too short trace: {yaml_path}")
        return None

    subnet_mapping, hostname_to_ip, ip_to_hostname = extract_subnet_mapping(data)
    steps = []

    # Discard last step since its result is unknown
    for i in range(len(data) - 1):
        current_step = data[i]
        next_step = data[i + 1]

        # Blue action
        blue_action = current_step['Blue']['action']
        blue_hostname = blue_action.get('hostname', '')
        blue_ip = hostname_to_ip.get(blue_hostname, '')
        blue_prev_status = next_step['Blue']['obs'].get('prev_action_status', 1)

        blue_dict = {
            'episode': episode_num,
            'step': i + 1,
            'action': blue_action['type'],
            'agent': 'Blue',
            'hostname': blue_hostname,
            'ip_address': blue_ip,
            'success': convert_prev_action_status(blue_prev_status)
        }

        # Red action
        red_action = current_step['Red']['action']
        red_prev_status = next_step['Red']['obs'].get('prev_action_status', 1)

        red_dict = {
            'episode': episode_num,
            'step': i + 1,
            'action': red_action['type'],
            'agent': 'Red',
            'success': convert_prev_action_status(red_prev_status)
        }

        # Add target info to Red action
        if 'subnet' in red_action:
            subnet_cidr = red_action['subnet']
            subnet_name, prefix = get_subnet_info(subnet_cidr, subnet_mapping)
            red_dict['subnetname'] = subnet_name
            red_dict['prefix_length'] = prefix

        if 'ip_address' in red_action:
            red_dict['ip_address'] = red_action['ip_address']
            if red_action['ip_address'] in ip_to_hostname:
                red_dict['hostname'] = ip_to_hostname[red_action['ip_address']]

        if 'hostname' in red_action:
            red_dict['hostname'] = red_action['hostname']
            if red_action['hostname'] in hostname_to_ip:
                red_dict['ip_address'] = hostname_to_ip[red_action['hostname']]

        if 'exploit_port' in red_action and red_action['exploit_port'] is not None:
            red_dict['exploit_port'] = red_action['exploit_port']

        if 'exploit_class' in red_action and red_action['exploit_class'] is not None:
            red_dict['exploit_class'] = red_action['exploit_class']

        steps.append([blue_dict, red_dict])

    return [steps]


def convert_single(args):
    """Worker function for parallel conversion."""
    idx, trace_path, output_dir = args
    try:
        result = convert_trace(trace_path, episode_num=1)
        if result:
            output_path = os.path.join(output_dir, f'output_{idx}.txt')
            with open(output_path, 'w') as f:
                f.write(repr(result))
            return (idx, True)
    except Exception as e:
        return (idx, False, str(e))
    return (idx, False)


def main():
    parser = argparse.ArgumentParser(description='Convert CybORG YAML traces to BabyCyborg format')
    parser.add_argument('source_dir', help='Directory containing raw YAML traces')
    parser.add_argument('output_dir', help='Output directory for converted traces')
    parser.add_argument('--max-traces', type=int, default=None, help='Maximum number of traces to convert')
    parser.add_argument('--scenario', default='cage2', help='Scenario filter (default: cage2)')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    # Find all matching YAML traces
    pattern = f'{args.source_dir}/*{args.scenario}*/**/trace_*.yaml'
    trace_files = sorted(glob.glob(pattern, recursive=True))
    print(f"Found {len(trace_files)} {args.scenario} traces in {args.source_dir}")

    if args.max_traces:
        trace_files = trace_files[:args.max_traces]
        print(f"Will convert first {args.max_traces}")

    # Convert in parallel
    work_items = [(i + 1, path, args.output_dir) for i, path in enumerate(trace_files)]
    num_workers = cpu_count()
    print(f"Converting with {num_workers} workers...")

    converted = 0
    failed = 0
    with Pool(num_workers) as pool:
        for result in pool.imap_unordered(convert_single, work_items, chunksize=50):
            if result[1]:
                converted += 1
            else:
                failed += 1
            if (converted + failed) % 500 == 0:
                print(f"  Progress: {converted + failed}/{len(trace_files)} (converted={converted}, failed={failed})")

    print(f"\nDone! Converted {converted} traces, {failed} failed")
    print(f"Output: {args.output_dir}/")


if __name__ == '__main__':
    main()
