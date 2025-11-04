from netmiko import ConnectHandler
import ipaddress
import re

def set_config(ip, username, password, int_name, new_ip, new_subnet, new_status):
    device = {
        "device_type": "cisco_ios",
        "host": ip,
        "username": username,
        "password": password,
    }

    status_cmd = "no shutdown" if new_status.lower() == "up" else "shutdown"
    commands = [
        f"interface {int_name}",
        f"ip address {new_ip} {new_subnet}",
        status_cmd,
        "exit",
        "write memory"
    ]

    try:
        with ConnectHandler(**device) as conn:
            conn.enable()
            output = conn.send_config_set(commands)
            conn.disconnect()

        output_lower = output.lower()
        success = "ok" in output_lower or "building configuration" in output_lower

    except Exception as e:
        print(f"[ERROR] Router config failed: {e}")
        success = False
        output = str(e)

    return success

def parse_route_table(raw_routes):
    routes = []
    for r in raw_routes:
        code = r.get("protocol") or "-"
        iface = r.get("interface") or "-"
        network = r.get("network") or "-"
        next_hop = r.get("nexthop_ip") or "Directly Connected"
        metric = r.get("metric") or 0
        age = r.get("age") or "-"

        proto_map = {
            "C": "Connected", "L": "Local", "S": "Static",
            "O": "OSPF", "D": "EIGRP", "B": "BGP"
        }

        routes.append({
            "code": code,
            "type": proto_map.get(code, "*"),
            "network": network,
            "next_hop": next_hop,
            "interface": iface,
            "metric": metric,
            "age": age
        })
    return routes

def cidr_to_mask(cidr):
    try:
        return str(ipaddress.ip_network("0.0.0.0" + cidr, strict=False).netmask)
    except Exception:
        return ""

def get_interfaces(ip, username, password):
    device = {
        "device_type": "cisco_ios",
        "host": ip,
        "username": username,
        "password": password,
    }

    result_int = []
    current_iface_data = None

    with ConnectHandler(**device) as conn:
        conn.enable()

        hostname_raw = conn.send_command("show run | include hostname")
        hostname_match = re.search(r"hostname\s+(\S+)", hostname_raw)
        hostname = hostname_match.group(1) if hostname_match else ip

        raw_detail = conn.send_command("show ip interface")

        for line in raw_detail.splitlines():
            line = line.strip()

            match_iface_line = re.match(r"^(\S+)\s+is\s+(.*?),?\s+line protocol is\s+(.*)", line)
            if match_iface_line:
                if current_iface_data:
                    result_int.append(current_iface_data)
                
                status_admin = match_iface_line.group(2).lower()
                status_line = match_iface_line.group(3).lower()
                
                final_status = "down"
                if status_admin == "up" and status_line == "up":
                    final_status = "up"
                elif "administratively down" in status_admin:
                    final_status = "admin down"

                current_iface_data = {
                    "interface": match_iface_line.group(1),
                    "status": final_status,
                    "ip_address": "unassign",
                    "subnet_mask": "unassign",
                    "description": ""
                }
                continue

            if current_iface_data and "Internet address is" in line:
                match_ip = re.search(r"Internet address is (\d+\.\d+\.\d+\.\d+)(/\d+)?", line)
                if match_ip:
                    ip_addr = match_ip.group(1)
                    prefix = match_ip.group(2) or ""
                    subnet_mask = cidr_to_mask(prefix) if prefix else "unassign"

                    current_iface_data["ip_address"] = ip_addr
                    current_iface_data["subnet_mask"] = subnet_mask

            if current_iface_data and "Description:" in line:
                match_desc = re.search(r"Description:\s*(.*)", line)
                if match_desc:
                    current_iface_data["description"] = match_desc.group(1)

        if current_iface_data:
            result_int.append(current_iface_data)

        result_route = conn.send_command("show ip route", use_textfsm=True)
        routes = parse_route_table(result_route)

        conn.disconnect()

    return hostname, result_int, routes