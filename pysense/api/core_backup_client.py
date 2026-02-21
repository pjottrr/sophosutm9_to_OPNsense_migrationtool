from typing import List, Optional

from pysense.base_client import BaseClient


class CoreBackupClient(BaseClient):

    def core_backup_backups(self, host: str = 'this') -> dict:
        """List available backups for a host."""
        return self._get(f'core/backup/backups/{host}')

    def core_backup_providers(self) -> dict:
        """List available backup providers."""
        return self._get('core/backup/providers')

    def core_backup_download(self, host: str = 'this', backup: str = None) -> str:
        """Download a backup config as XML string.

        Args:
            host: Backup provider host (default 'this' for local).
            backup: Specific backup name/timestamp. If None, downloads current config.

        Returns:
            XML config content as string.
        """
        endpoint = f'core/backup/download/{host}'
        if backup:
            endpoint += f'/{backup}'
        return self._get(endpoint, raw=True)

    def core_backup_download_to_file(self, path: str, host: str = 'this', backup: str = None) -> str:
        """Download a backup config and save it to a local file.

        Args:
            path: Local file path to save the config to.
            host: Backup provider host (default 'this' for local).
            backup: Specific backup name/timestamp. If None, downloads current config.

        Returns:
            The file path written to.
        """
        content = self.core_backup_download(host=host, backup=backup)
        with open(path, 'w') as f:
            f.write(content)
        return path

    def core_backup_diff(self, host: str, backup1: str, backup2: str) -> str:
        """Get diff between two backups.

        Args:
            host: Backup provider host.
            backup1: First backup identifier.
            backup2: Second backup identifier.

        Returns:
            Diff output as string.
        """
        return self._get(f'core/backup/diff/{host}/{backup1}/{backup2}', raw=True)

    def core_backup_delete(self, backup: str) -> dict:
        """Delete a backup.

        Args:
            backup: Backup identifier to delete.

        Returns:
            API response dict.
        """
        return self._post('core/backup/delete_backup', {'backup': backup})

    def core_backup_revert(self, backup: str) -> dict:
        """Revert to a specific backup.

        Args:
            backup: Backup identifier to revert to.

        Returns:
            API response dict.
        """
        return self._post('core/backup/revert_backup', {'backup': backup})
