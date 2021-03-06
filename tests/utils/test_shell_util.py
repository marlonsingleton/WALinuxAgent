# -*- coding: utf-8 -*-
# Copyright 2018 Microsoft Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Requires Python 2.6+ and Openssl 1.0+
#

from tests.tools import *
import uuid
import unittest
import os
import azurelinuxagent.common.utils.shellutil as shellutil
import test


class ShellQuoteTestCase(AgentTestCase):
    def test_shellquote(self):
        self.assertEqual("\'foo\'", shellutil.quote("foo"))
        self.assertEqual("\'foo bar\'", shellutil.quote("foo bar"))
        self.assertEqual("'foo'\\''bar'", shellutil.quote("foo\'bar"))


class RunTestCase(AgentTestCase):
    def test_it_should_return_the_exit_code_of_the_command(self):
        exit_code = shellutil.run("exit 123")
        self.assertEquals(123, exit_code)

    def test_it_should_be_a_pass_thru_to_run_get_output(self):
        with patch.object(shellutil, "run_get_output", return_value=(0, "")) as mock_run_get_output:
            shellutil.run("echo hello word!", chk_err=False, expected_errors=[1, 2, 3])

        self.assertEquals(mock_run_get_output.call_count, 1)

        args, kwargs = mock_run_get_output.call_args
        self.assertEquals(args[0], "echo hello word!")
        self.assertEquals(kwargs["chk_err"], False)
        self.assertEquals(kwargs["expected_errors"], [1, 2, 3])


class RunGetOutputTestCase(AgentTestCase):
    def test_run_get_output(self):
        output = shellutil.run_get_output(u"ls /")
        self.assertNotEquals(None, output)
        self.assertEquals(0, output[0])

        err = shellutil.run_get_output(u"ls /not-exists")
        self.assertNotEquals(0, err[0])
            
        err = shellutil.run_get_output(u"ls 我")
        self.assertNotEquals(0, err[0])

    def test_it_should_log_the_command(self):
        command = "echo hello world!"

        with patch("azurelinuxagent.common.utils.shellutil.logger", autospec=True) as mock_logger:
            shellutil.run_get_output(command)

        self.assertEquals(mock_logger.verbose.call_count, 1)

        args, kwargs = mock_logger.verbose.call_args
        command_in_message = args[1]
        self.assertEqual(command_in_message, command)


    def test_it_should_log_command_failures_as_errors(self):
        return_code = 99
        command = "exit {0}".format(return_code)

        with patch("azurelinuxagent.common.utils.shellutil.logger", autospec=True) as mock_logger:
            shellutil.run_get_output(command, log_cmd=False)

        self.assertEquals(mock_logger.error.call_count, 1)

        args, kwargs = mock_logger.error.call_args
        message = args[0]  # message is similar to "Command: [exit 99], return code: [99], result: []"
        self.assertIn("[{0}]".format(command), message)
        self.assertIn("[{0}]".format(return_code), message)

        self.assertEquals(mock_logger.verbose.call_count, 0)
        self.assertEquals(mock_logger.info.call_count, 0)
        self.assertEquals(mock_logger.warn.call_count, 0)

    def test_it_should_log_expected_errors_as_info(self):
        return_code = 99
        command = "exit {0}".format(return_code)

        with patch("azurelinuxagent.common.utils.shellutil.logger", autospec=True) as mock_logger:
            shellutil.run_get_output(command, log_cmd=False, expected_errors=[return_code])

        self.assertEquals(mock_logger.info.call_count, 1)

        args, kwargs = mock_logger.info.call_args
        message = args[0]  # message is similar to "Command: [exit 99], return code: [99], result: []"
        self.assertIn("[{0}]".format(command), message)
        self.assertIn("[{0}]".format(return_code), message)

        self.assertEquals(mock_logger.verbose.call_count, 0)
        self.assertEquals(mock_logger.warn.call_count, 0)
        self.assertEquals(mock_logger.error.call_count, 0)

    def test_it_should_log_unexpected_errors_as_errors(self):
        return_code = 99
        command = "exit {0}".format(return_code)

        with patch("azurelinuxagent.common.utils.shellutil.logger", autospec=True) as mock_logger:
            shellutil.run_get_output(command, log_cmd=False, expected_errors=[return_code + 1])

        self.assertEquals(mock_logger.error.call_count, 1)

        args, kwargs = mock_logger.error.call_args
        message = args[0]  # message is similar to "Command: [exit 99], return code: [99], result: []"
        self.assertIn("[{0}]".format(command), message)
        self.assertIn("[{0}]".format(return_code), message)

        self.assertEquals(mock_logger.info.call_count, 0)
        self.assertEquals(mock_logger.verbose.call_count, 0)
        self.assertEquals(mock_logger.warn.call_count, 0)


if __name__ == '__main__':
    unittest.main()
