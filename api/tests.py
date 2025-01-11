import os

import unittest
from unittest.mock import patch, MagicMock
import json
from app import app

class TestRestaurantAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    @patch('psycopg2.connect')
    def test_add_restaurant(self, mock_connect):
        os.environ["AUTH_ENDPOINT"] = "http://mock_auth_endpoint"

        # Mock the context managers
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [1]

        test_data = {
            "name": "Test Restaurant",
            "type": "Italian",
            "rating": 4.5,
            "address": "123 Test St",
            "average_time": 30,
            "price_range": "$$",
            "user_id": 1
        }

        response = self.app.post('/add_restaurant',
                               data=json.dumps(test_data),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['restaurant_id'], 1)

    @patch('psycopg2.connect')
    def test_get_restaurants(self, mock_connect):
        # Mock the context managers
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(1, "Test Restaurant", "Italian", 4.5, "123 Test St", 30, "$$")]

        response = self.app.get('/get_restaurants')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(len(response_data['resturant_list']), 1)
        self.assertEqual(response_data['resturant_list'][0][1], "Test Restaurant")

    @patch('psycopg2.connect')
    def test_add_menu_item(self, mock_connect):
        # Mock the context managers
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [1]

        test_data = {
            "name": "Spaghetti",
            "price": 12.99
        }

        response = self.app.post('/add_menu_item',
                               data=json.dumps(test_data),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['menu_item'][0], 1)
        self.assertEqual(response_data['menu_item'][1], "Spaghetti")

    @patch('psycopg2.connect')
    def test_get_menu_items(self, mock_connect):
        # Mock the context managers
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(1, "Spaghetti", 12.99)]

        response = self.app.get('/get_menu_items')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(len(response_data['menu_items']), 1)
        self.assertEqual(response_data['menu_items'][0][1], "Spaghetti")

    @patch('psycopg2.connect')
    def test_add_menu(self, mock_connect):
        # Mock the context managers
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [1]

        test_data = {
            "restaurant_id": 1,
            "items": [1, 2, 3]
        }

        response = self.app.post('/add_menu',
                               data=json.dumps(test_data),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['menu_id'], 1)

    @patch('psycopg2.connect')
    def test_get_menu_by_id(self, mock_connect):
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.__enter__.return_value = mock_cursor
        
        # Mock the first query that gets the menu
        mock_cursor.fetchone.side_effect = [
            (1, 1, [1, 2, 3]),  # First fetchone returns menu with item IDs
            (1,),  # Second fetchone for first menu item
            (2,),  # Third fetchone for second menu item
            (3,)   # Fourth fetchone for third menu item
        ]

        response = self.app.get('/get_menu_by_id?restaurant_id=1')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['menu_items'], [[1], [2], [3]])
        
        # Verify the SQL queries were called correctly
        mock_cursor.execute.assert_any_call("SELECT * FROM menus WHERE restaurant_id = %s", ('1',))
        mock_cursor.execute.assert_any_call("SELECT * FROM menu_items WHERE id = %s", (1,))
        mock_cursor.execute.assert_any_call("SELECT * FROM menu_items WHERE id = %s", (2,))
        mock_cursor.execute.assert_any_call("SELECT * FROM menu_items WHERE id = %s", (3,))

if __name__ == '__main__':
    unittest.main()