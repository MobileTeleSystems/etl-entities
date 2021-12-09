from __future__ import annotations

from pydantic import validator

from etl_entities.entity import BaseModel, Entity
from etl_entities.location import AbsolutePath, RemoteURL

# root path cannot have delimiters used in qualified_name
PROHIBITED_ROOT_SYMBOLS = "@#"


class RemoteFolder(BaseModel, Entity):
    """Remote folder representation

    Parameters
    ----------
    root : :obj:`str` or :obj:`pathlib.PosixPath`

        Folder root path

        .. warning::

            Only absolute path without ``..`` are allowed

    instance : :obj:`etl_entities.location.url.remote_url.RemoteURL`

        Instance URL in format ``"protocol://some.domain[:port]"``

    Examples
    ----------

    .. code:: python

        from etl_entities import RemoteFolder

        folder = RemoteFolder(root="/root/folder", location="hdfs://some.domain:10000")
    """

    root: AbsolutePath
    location: RemoteURL

    @validator("root", pre=True)
    def check_absolute_path(cls, value):  # noqa: N805
        value = AbsolutePath(value)

        for symbol in PROHIBITED_ROOT_SYMBOLS:
            if symbol in str(value):
                raise ValueError(f"Root path cannot contain symbols {' '.join(PROHIBITED_ROOT_SYMBOLS)}")

        return value

    @property
    def name(self) -> str:
        """
        Folder name

        Returns
        ----------
        value : str

            Folder base name

        Examples
        ----------

        .. code:: python

            from etl_entities import RemoteFolder

            folder = RemoteFolder(root="/root/folder", location="hdfs://some.domain:10000")

            assert folder.name == "folder"
        """

        return self.root.name

    def __str__(self):
        """
        Returns root path
        """

        return str(self.root)

    @property
    def qualified_name(self) -> str:
        """
        Unique name of remote folder

        Returns
        ----------
        value : str

            Qualified name

        Examples
        ----------

        .. code:: python

            from etl_entities import RemoteFolder

            folder = RemoteFolder(root="/root/folder", location="hdfs://some.domain:10000")

            assert folder.qualified_name == "/root/folder@hdfs://some.domain:10000"
        """

        return "@".join([str(self), str(self.location)])
