"""

Test custom Gjango management commands.
"""

from unittest.mock import patch
from psycopg2 import OperationalError as Psycog2Error
from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase

# we're patching the check method of the Command class in the wait_for_db module. This means that during your tests, any call to self.check in the Command class will be replaced by a mock object.
@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):

    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for database if database ready."""
        patched_check.return_value= True

        call_command('wait_for_db')

        patched_check.assert_called_once_with(databases=['default'])

    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Test waiting for database when getting OperationalError."""
        # raise 5 errors then true
        patched_check.side_effect = [Psycog2Error] * 2 + [OperationalError] * 3 + [True]
        
        call_command('wait_for_db')

        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=['default'])