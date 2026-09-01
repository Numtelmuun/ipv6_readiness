"""Vendor-neutral IPv6 Readiness Checklist v1.0 rules."""

from models.device import DeviceInfo

ALIASES = {"ospf": "ospfv3", "ospfv3": "ospfv3", "is-is": "isis", "isis": "isis",
           "bgp": "bgp_ipv6", "bgp ipv6": "bgp_ipv6", "ipv6 bgp": "bgp_ipv6",
           "bgp_ipv6": "bgp_ipv6", "ripng": "ripng", "eigrpv6": "eigrpv6"}
# Preserve the legacy 100-point allocation; readiness no longer uses thresholds.
WEIGHTS = dict(zip((f"IPV6-{i:02d}" for i in range(1, 10)), (20, 15, 10, 20, 15, 5, 5, 5, 5)))


def _protocols(values):
    return {ALIASES.get(str(v).strip().lower(), str(v).strip().lower()) for v in (values or [])}


def required_protocols(device):
    return _protocols(device.required_routing_protocols)


def detected_protocols(device):
    found = _protocols(device.routing.ipv6_protocols)
    found.update(p for p in ("ospfv3", "ripng", "eigrpv6", "bgp_ipv6")
                 if getattr(device.routing, p, False))
    return found


def finding(cid, name, status, category, message, remediation="NONE", evidence=None,
            failure_kind=None):
    result = {"id": cid, "name": name, "status": status, "category": category,
              "message": message, "evidence": evidence or [], "remediation": remediation,
              "score": WEIGHTS[cid] if status == "PASS" else 0, "max_score": WEIGHTS[cid]}
    if failure_kind:
        result["failure_kind"] = failure_kind
    return result


def _l2(device):
    return device.device_type.lower() in {"l2", "layer2", "layer-2", "l2_switch"}


def check_basic_capability(d):
    ev = [f"platform={d.platform}", f"model={d.model}", f"os_version={d.os_version}"]
    if d.ipv6_supported is True:
        return finding("IPV6-01", "Basic IPv6 capability", "PASS", "CAPABILITY",
                       "Basic IPv6 support is positively confirmed.", evidence=ev)
    if d.ipv6_supported is False:
        return finding("IPV6-01", "Basic IPv6 capability", "FAIL", "CAPABILITY",
                       "Basic IPv6 capability is explicitly unavailable.", "UPGRADE_OR_REPLACE", ev,
                       "capability_unsupported")
    return finding("IPV6-01", "Basic IPv6 capability", "UNKNOWN", "CAPABILITY",
                   "Available evidence is insufficient to determine basic IPv6 support.", "VERIFY", ev)


def check_addressing_capability(d):
    if d.ipv6_addressing_capable is True:
        return finding("IPV6-02", "IPv6 addressing capability", "PASS", "CAPABILITY",
                       "IPv6 addresses can be configured and represented.")
    if d.ipv6_addressing_capable is False:
        return finding("IPV6-02", "IPv6 addressing capability", "FAIL", "CAPABILITY",
                       "IPv6 addressing capability is explicitly unsupported.", "UPGRADE_OR_REPLACE",
                       failure_kind="capability_unsupported")
    return finding("IPV6-02", "IPv6 addressing capability", "UNKNOWN", "CAPABILITY",
                   "IPv6 addressing capability could not be established.", "VERIFY")


def _required(d):
    if d.required_ipv6_interfaces is None:
        return None
    interfaces = {i.name: i for i in d.interfaces}
    return [(name, interfaces.get(name)) for name in d.required_ipv6_interfaces]


def check_interface_configuration(d):
    req = _required(d)
    if req is None:
        return finding("IPV6-03", "IPv6 interface configuration", "UNKNOWN", "CONFIGURATION",
                       "Required IPv6 interfaces cannot be determined from design data.", "VERIFY")
    if not req:
        return finding("IPV6-03", "IPv6 interface configuration", "NOT_APPLICABLE", "CONFIGURATION",
                       "No IPv6 interface requirement exists for this device role/design.")
    states = [i.ipv6_enabled if i else None for _, i in req]
    names = [n for n, _ in req]
    if all(s is True for s in states):
        return finding("IPV6-03", "IPv6 interface configuration", "PASS", "CONFIGURATION",
                       "All required interfaces are configured for IPv6.", evidence=names)
    if any(s is True for s in states):
        return finding("IPV6-03", "IPv6 interface configuration", "WARNING", "CONFIGURATION",
                       "Only some required interfaces are configured for IPv6.", "CONFIGURE", names)
    if any(s is None for s in states):
        return finding("IPV6-03", "IPv6 interface configuration", "UNKNOWN", "CONFIGURATION",
                       "State is unavailable for one or more required interfaces.", "VERIFY", names)
    return finding("IPV6-03", "IPv6 interface configuration", "FAIL", "CONFIGURATION",
                   "Required interfaces are not configured for IPv6.", "CONFIGURE", names,
                   "configuration_missing")


def check_link_local(d):
    req = _required(d)
    if req is None:
        return finding("IPV6-04", "IPv6 link-local operation", "UNKNOWN", "CONFIGURATION",
                       "Required interfaces cannot be determined.", "VERIFY")
    enabled = [(n, i) for n, i in req if i and i.ipv6_enabled is True]
    if not enabled:
        return finding("IPV6-04", "IPv6 link-local operation", "NOT_APPLICABLE", "CONFIGURATION",
                       "No required IPv6-enabled interface is available to evaluate.")
    missing = [n for n, i in enabled if not i.link_local]
    if missing:
        return finding("IPV6-04", "IPv6 link-local operation", "FAIL", "CONFIGURATION",
                       "Expected link-local operation is absent.", "CONFIGURE", missing,
                       "configuration_missing")
    return finding("IPV6-04", "IPv6 link-local operation", "PASS", "CONFIGURATION",
                   "Required IPv6-enabled interfaces have link-local addresses/state.",
                   evidence=[n for n, _ in enabled])


def check_forwarding(d):
    if _l2(d):
        return finding("IPV6-05", "IPv6 forwarding", "NOT_APPLICABLE", "CAPABILITY_CONFIGURATION",
                       "IPv6 L3 forwarding is not required for this L2 device.")
    if d.ipv6_forwarding_capable is False:
        return finding("IPV6-05", "IPv6 forwarding", "FAIL", "CAPABILITY_CONFIGURATION",
                       "IPv6 forwarding capability is explicitly unsupported.", "UPGRADE_OR_REPLACE",
                       failure_kind="capability_unsupported")
    if d.ipv6_forwarding_capable is True and d.ipv6_routing_enabled is False:
        return finding("IPV6-05", "IPv6 forwarding", "FAIL", "CAPABILITY_CONFIGURATION",
                       "IPv6 forwarding is supported but disabled.", "CONFIGURE",
                       failure_kind="configuration_disabled")
    if d.ipv6_forwarding_capable is True and d.ipv6_routing_enabled is True:
        return finding("IPV6-05", "IPv6 forwarding", "PASS", "CAPABILITY_CONFIGURATION",
                       "IPv6 forwarding capability is available and forwarding is enabled.")
    return finding("IPV6-05", "IPv6 forwarding", "UNKNOWN", "CAPABILITY_CONFIGURATION",
                   "IPv6 forwarding capability or state could not be determined.", "VERIFY")


def check_routing_table(d):
    if _l2(d):
        return finding("IPV6-06", "IPv6 routing table capability", "NOT_APPLICABLE",
                       "CAPABILITY_OPERATIONAL", "IPv6 L3 routing is not required for this L2 device.")
    ev = [f"routes={d.routing.route_count}", f"connected={d.routing.connected_routes}",
          f"local={d.routing.local_routes}"]
    if d.ipv6_routing_table_capable is True:
        return finding("IPV6-06", "IPv6 routing table capability", "PASS", "CAPABILITY_OPERATIONAL",
                       "IPv6 routing table capability is confirmed.", evidence=ev)
    if d.ipv6_routing_table_capable is False:
        return finding("IPV6-06", "IPv6 routing table capability", "FAIL", "CAPABILITY_OPERATIONAL",
                       "IPv6 routing capability is explicitly unavailable.", "UPGRADE_OR_REPLACE", ev,
                       "capability_unsupported")
    return finding("IPV6-06", "IPv6 routing table capability", "UNKNOWN", "CAPABILITY_OPERATIONAL",
                   "IPv6 routing table capability could not be established.", "VERIFY", ev)


def _routing(d, cid, name, wanted, na_message):
    req = required_protocols(d) & wanted
    if not req:
        return finding(cid, name, "NOT_APPLICABLE", "ROUTING", na_message)
    missing = req - detected_protocols(d)
    if not missing:
        return finding(cid, name, "PASS", "ROUTING", "Required IPv6 routing protocol is configured.",
                       evidence=sorted(req))
    if d.supported_routing_protocols is None:
        return finding(cid, name, "UNKNOWN", "ROUTING",
                       "A required protocol is not configured and its capability is unknown.", "VERIFY",
                       sorted(missing))
    unsupported = missing - _protocols(d.supported_routing_protocols)
    if unsupported:
        return finding(cid, name, "FAIL", "ROUTING", "A required protocol is explicitly unsupported.",
                       "UPGRADE_OR_REPLACE", sorted(unsupported), "capability_unsupported")
    return finding(cid, name, "FAIL", "ROUTING", "A required supported protocol is not configured.",
                   "CONFIGURE", sorted(missing), "configuration_missing")


def check_required_igp(d):
    return _routing(d, "IPV6-07", "Required IPv6 IGP", {"ospfv3", "isis", "ripng", "eigrpv6"},
                    "No IPv6 IGP is required for this device.")


def check_required_bgp(d):
    return _routing(d, "IPV6-08", "Required IPv6 BGP", {"bgp_ipv6"},
                    "IPv6 BGP is not required for this device.")


def check_interface_coverage(d):
    req = _required(d)
    if req is None:
        return finding("IPV6-09", "Required interface coverage", "UNKNOWN", "CONFIGURATION",
                       "The required L3 interface set is unavailable.", "VERIFY")
    if not req:
        return finding("IPV6-09", "Required interface coverage", "NOT_APPLICABLE", "CONFIGURATION",
                       "The topology/design does not require interface coverage.")
    unconfigured = [n for n, i in req if i is not None and i.ipv6_enabled is False]
    if unconfigured:
        return finding("IPV6-09", "Required interface coverage", "FAIL", "CONFIGURATION",
                       "Known required L3 interfaces are not configured for IPv6.", "CONFIGURE",
                       unconfigured, "configuration_missing")
    if any(i is None or i.ipv6_enabled is None or i.operational is None for _, i in req):
        return finding("IPV6-09", "Required interface coverage", "UNKNOWN", "CONFIGURATION",
                       "Required interface readiness cannot be fully determined.", "VERIFY",
                       [n for n, _ in req])
    down = [n for n, i in req if i.operational is False]
    if down:
        return finding("IPV6-09", "Required interface coverage", "WARNING", "CONFIGURATION",
                       "Required interfaces are IPv6-configured but operationally down.", "VERIFY",
                       down)
    return finding("IPV6-09", "Required interface coverage", "PASS", "CONFIGURATION",
                   "All required IPv6 interfaces are configured and operational.",
                   evidence=[n for n, _ in req])


CHECKLIST_RULES = [check_basic_capability, check_addressing_capability,
                   check_interface_configuration, check_link_local, check_forwarding,
                   check_routing_table, check_required_igp, check_required_bgp,
                   check_interface_coverage]
