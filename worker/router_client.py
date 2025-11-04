from netmiko import ConnectHandler
import re

def set_config(ip, username, password, int_name, new_ip, new_subnet, new_status):
    device = {
        "device_type": "cisco_ios",
        "host": ip,
        "username": username,
        "password": password,
    }

    if new_status.lower() == "down":
        status_cmd = "shutdown"
    else:
        status_cmd = "no shutdown"

    commands = [
        f"interface {int_name}",
        f"ip address {new_ip} {new_subnet}",
        status_cmd,
        "exit",
        "write memory"
    ]

    with ConnectHandler(**device) as conn:
        conn.enable()
        output = conn.send_config_set(commands)
        conn.disconnect()

    return output

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

def get_interfaces(ip, username, password):
    device = {
        "device_type": "cisco_ios",
        "host": ip,
        "username": username,
        "password": password,
    }

    with ConnectHandler(**device) as conn:
        conn.enable()

        hostname_raw = conn.send_command("show run | include hostname")
        hostname_match = re.search(r"hostname\s+(\S+)", hostname_raw)
        hostname = hostname_match.group(1) if hostname_match else ip

        result_int = conn.send_command("show ip int br", use_textfsm=True)
        for i in result_int:
            i["description"] = i.get("interface")
            i["status"] = i.get("status").lower()

        result_route = conn.send_command("show ip route", use_textfsm=True)
        routes = parse_route_table(result_route)

        conn.disconnect()

    return hostname, result_int, routes
