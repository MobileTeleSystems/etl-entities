from __future__ import annotations

from ipaddress import ip_address

from hwmlib.location.url.generic_url import GenericURL


class RemoteURL(GenericURL):
    """Remote URL representation

    Same as :obj:hwmlib.location.url.generic_url.GenericURL`, but with some restrictions for host name.

    .. warning::

        If name is domain name, it cannot be ``localhost``.

        If name is IP address, it cannot be:

            * loopback interface, e.g. ``127.0.0.1`` or ``::1``
            * broadcast address, e.g. `255.255.255.255`` or ``ff00::``
            * network address, e.g. ``0.0.0.0`` or ``::``
            * reserved address , e.g. ``240.0.0.0``
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "localhost" in self.host:
            raise ValueError("localhost is not valid host name")

        if self.host_type in {"ipv4", "ipv6"}:
            ip = ip_address(self.host)

            conditions = [
                ip.is_link_local,
                ip.is_loopback,
                ip.is_multicast,
                ip.is_unspecified,
                ip.is_reserved,
            ]

            if any(conditions):
                raise ValueError(f"{self.host} cannot be a remote host name")
