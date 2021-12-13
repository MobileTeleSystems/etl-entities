from __future__ import annotations

import logging
import os
from socket import getfqdn

import psutil
from pydantic import AnyUrl, Field, parse_obj_as, validator
from pydantic.validators import str_validator

from etl_entities.entity import BaseModel, Entity

log = logging.getLogger(__name__)


class Process(BaseModel, Entity):
    """Process representation

    Parameters
    ----------
    name : :obj:`str`, default: current process name

        Process name

    host : :obj:`str`, default: current host FQDN

        Host name. Could be hostname, FQDN or IPv4/IPv6 address

    Examples
    ----------

    .. code:: python

        from etl_entities import Process

        process = Process()
        process1 = Process(name="mycolumn")
        process2 = Process(name="mycolumn", host="myhost")
    """

    name: str = Field(default_factory=lambda: psutil.Process(os.getpid()).name())
    host: str = Field(default_factory=getfqdn)

    @validator("host", pre=True)
    def validate_host(cls, value):  # noqa: N805
        value = str_validator(value).strip()
        if not value:
            raise ValueError("Empty hostname")

        url = parse_obj_as(AnyUrl, f"http://{value}")
        if url.host != value:
            raise ValueError("Invalid host")

        return value

    def __str__(self):
        """
        Returns process name
        """

        return self.name

    @property
    def qualified_name(self) -> str:
        """
        Unique name of process

        Returns
        ----------
        value : str

            Qualified name

        Examples
        ----------

        .. code:: python

            from etl_entities import Process

            process = Process(name="mycolumn", host="myhost")

            assert process.qualified_name == "currentapp@somehost"
        """

        return "@".join([self.name, self.host])

    def __enter__(self):
        """
        Enter the process context

        Examples
        ----------

        .. code:: python

            from etl_entities import Process

            with Process(name="mycolumn", host="myhost") as process:
                ...
        """

        # hack to avoid circular imports
        from etl_entities.process.process_stack_manager import ProcessStackManager

        log.debug(f"{self.__class__.__name__}: Entered stack at level {ProcessStackManager.get_current_level()}")
        ProcessStackManager.push(self)
        log.info(f"{self.__class__.__name__}: Using process {self}")
        return self

    def __exit__(self, exc_type, _exc_value, _traceback):
        from etl_entities.process.process_stack_manager import ProcessStackManager

        log.debug(f"{self.__class__.__name__}: Exiting stack at level {ProcessStackManager.get_current_level()-1}")
        ProcessStackManager.pop()
        return False
