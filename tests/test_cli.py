import pytest
from unittest.mock import patch, MagicMock
import argparse
from auto_clicker.cli import parse_args, main

class TestCLI:
    def test_parse_args_defaults(self):
        """Test argument parsing with default values."""
        with patch('argparse.ArgumentParser.parse_args',
                  return_value=argparse.Namespace(cps=500, key='c', mouse=None)):
            args = parse_args()
            assert args.cps == 500
            assert args.key == 'c'
            assert args.mouse is None
    
    def test_parse_args_custom(self):
        """Test argument parsing with custom values."""
        with patch('sys.argv', ['auto_clicker', '--cps', '100', '--key', 'x', '--mouse', 'right']):
            args = parse_args()
            assert args.cps == 100
            assert args.key == 'x'
            assert args.mouse == 'right'
    
    def test_main_function(self):
        """Test the main function."""
        mock_auto_clicker = MagicMock()
        
        with patch('auto_clicker.cli.parse_args') as mock_parse_args, \
             patch('auto_clicker.cli.AutoClicker', return_value=mock_auto_clicker):
            
            # Configure mock args
            mock_args = MagicMock()
            mock_args.cps = 200
            mock_args.key = 'z'
            mock_args.mouse = 'middle'
            mock_parse_args.return_value = mock_args
            
            # Call main function
            main()
            
            # Verify AutoClicker instantiated and started correctly
            mock_auto_clicker.start.assert_called_once()