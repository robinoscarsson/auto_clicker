import pytest
from unittest.mock import MagicMock, patch
from pynput import keyboard, mouse
import threading
import time

from auto_clicker.clicker import AutoClicker

@pytest.fixture
def auto_clicker():
    """Create a basic AutoClicker instance with mocked controllers."""
    with patch('auto_clicker.clicker.mouse.Controller') as mouse_controller_mock:
        ac = AutoClicker(cps=10, toggle_key='c')
        yield ac

class TestAutoClicker:
    
    def test_initialization_default(self):
        """Test initialization with default parameters."""
        with patch('auto_clicker.clicker.mouse.Controller'):
            ac = AutoClicker()
            assert ac.cps == 500
            assert ac.click_interval == 0.002
            assert ac.toggle_key == 'c'
            assert ac.toggle_key_name == 'C'
            assert ac.toggle_mouse_button is None
            assert not ac._clicking_event.is_set()
            assert not ac._stop_event.is_set()
    
    def test_initialization_custom(self):
        """Test initialization with custom parameters."""
        with patch('auto_clicker.clicker.mouse.Controller'):
            ac = AutoClicker(cps=100, toggle_key='x', toggle_mouse_button='right')
            assert ac.cps == 100
            assert ac.click_interval == 0.01  # 1/100
            assert ac.toggle_key == 'x'
            assert ac.toggle_key_name == 'X'
            assert ac.toggle_mouse_button == mouse.Button.right
            assert ac.toggle_mouse_button_name == "RIGHT"
    
    def test_invalid_cps(self):
        """Test handling of invalid CPS values."""
        with patch('auto_clicker.clicker.mouse.Controller'), \
             patch('builtins.print') as mock_print:
            # Test negative CPS
            ac = AutoClicker(cps=-5)
            assert ac.cps == 500  # Verify that default CPS is used
            assert ac.click_interval == 0.002  # Verify the correct interval

            # Check that print was called, but don't assert the exact message
            # since it's printing the configured interval, not an error message
            assert mock_print.called
            
            # Alternative approach: check the specific message if you know it
            mock_print.assert_any_call('Click interval: 0.002 seconds (500 CPS)')
    
    def test_toggle_clicking(self, auto_clicker):
        """Test toggling the clicking state."""
        with patch.object(auto_clicker, 'simulate_mouse_click') as mock_simulate:
            # Mock the thread creation
            with patch('threading.Thread') as mock_thread_class:
                mock_thread = MagicMock()
                mock_thread_class.return_value = mock_thread
                
                # Start clicking
                auto_clicker.toggle_clicking()
                assert auto_clicker._clicking_event.is_set()
                mock_thread_class.assert_called_once()
                mock_thread.start.assert_called_once()
                
                # Stop clicking
                auto_clicker.toggle_clicking()
                assert not auto_clicker._clicking_event.is_set()
    
    def test_on_press_character_key(self, auto_clicker):
        """Test key press handler with character key."""
        with patch.object(auto_clicker, 'toggle_clicking') as mock_toggle:
            # Create a mock key with the toggle character
            key_mock = MagicMock()
            key_mock.char = 'c'  # Default toggle key
            
            auto_clicker.on_press(key_mock)
            mock_toggle.assert_called_once()
            
            # Test with different character
            mock_toggle.reset_mock()
            key_mock.char = 'x'
            auto_clicker.on_press(key_mock)
            mock_toggle.assert_not_called()
    
    def test_on_click(self, auto_clicker):
        """Test mouse click handler."""
        # Set up auto_clicker with mouse toggle
        auto_clicker.toggle_mouse_button = mouse.Button.right
        
        with patch.object(auto_clicker, 'toggle_clicking') as mock_toggle:
            # Test with correct button when pressed
            auto_clicker.on_click(100, 200, mouse.Button.right, True)
            mock_toggle.assert_called_once()
            
            # Test with correct button when released
            mock_toggle.reset_mock()
            auto_clicker.on_click(100, 200, mouse.Button.right, False)
            mock_toggle.assert_not_called()
            
            # Test with different button
            mock_toggle.reset_mock()
            auto_clicker.on_click(100, 200, mouse.Button.left, True)
            mock_toggle.assert_not_called()
    
    def test_on_release(self, auto_clicker):
        """Test key release handler."""
        # Test with Escape key
        with patch('builtins.print'):
            result = auto_clicker.on_release(keyboard.Key.esc)
        assert result is False  # Should return False to stop listener
        assert auto_clicker._stop_event.is_set()
        assert not auto_clicker._clicking_event.is_set()
        
        # Reset for next test
        auto_clicker._stop_event.clear()
        auto_clicker._clicking_event.set()
        
        # Test with another key
        result = auto_clicker.on_release(keyboard.Key.space)
        assert result is None  # Should not return anything specific
        assert auto_clicker._clicking_event.is_set()  # Should remain unchanged
        assert not auto_clicker._stop_event.is_set()  # Should remain unchanged
    
    def test_cleanup(self, auto_clicker):
        """Test cleanup method."""
        # Create a mock thread
        mock_thread = MagicMock()
        auto_clicker.click_thread = mock_thread
        auto_clicker._clicking_event.set()
        
        with patch('builtins.print'):
            auto_clicker.cleanup()
        
        assert auto_clicker._stop_event.is_set()
        assert not auto_clicker._clicking_event.is_set()
        mock_thread.join.assert_called_once_with(timeout=1.0)
    
    @patch('auto_clicker.clicker.keyboard.Listener')
    @patch('auto_clicker.clicker.mouse.Listener')
    def test_start(self, mock_mouse_listener, mock_keyboard_listener, auto_clicker):
        """Test start method."""
        # Set up mocks
        mock_keyboard_instance = MagicMock()
        mock_mouse_instance = MagicMock()
        mock_keyboard_listener.return_value = mock_keyboard_instance
        mock_mouse_listener.return_value = mock_mouse_instance
        
        # Mock print to avoid output during tests
        with patch('builtins.print'):
            auto_clicker.start()
        
        # Check listeners created and started correctly
        mock_keyboard_listener.assert_called_once()
        mock_mouse_listener.assert_called_once()
        mock_keyboard_instance.start.assert_called_once()
        mock_mouse_instance.start.assert_called_once()
        
        # Check both listeners are stopped in cleanup
        mock_keyboard_instance.stop.assert_called_once()
        mock_mouse_instance.stop.assert_called_once()
    
    @patch('auto_clicker.clicker.keyboard.Listener')
    @patch('auto_clicker.clicker.mouse.Listener')
    def test_start_exception_safety(self, mock_mouse_listener, mock_keyboard_listener, auto_clicker):
        """Test that start() handles exceptions during listener creation safely."""
        # Set up keyboard listener to succeed
        mock_keyboard_instance = MagicMock()
        mock_keyboard_listener.return_value = mock_keyboard_instance
        
        # Set up mouse listener to fail during creation
        mock_mouse_listener.side_effect = Exception("Mouse listener creation failed")
        
        # Should not raise, should clean up keyboard listener
        with patch('builtins.print'):
            with pytest.raises(Exception, match="Mouse listener creation failed"):
                auto_clicker.start()
        
        # Keyboard listener should still be stopped in cleanup
        mock_keyboard_instance.stop.assert_called_once()