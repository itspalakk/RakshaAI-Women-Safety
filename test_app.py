"""
test_app.py — Complete end-to-end integration test for RakshaAI server routes.
"""
import sys
import os

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import unittest
from app import app


class TestRakshaAIApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_01_index_route(self):
        """Verify the main UI loads successfully."""
        res = self.app.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'AlertMe', res.data)
        self.assertIn(b'Smart Emergency SOS', res.data)

    def test_02_ping_route(self):
        """Verify ping endpoint reports server and config health."""
        res = self.app.get('/ping')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get('status'), 'ok')
        self.assertIn('twilio_sid_loaded', data)

    def test_03_my_location(self):
        """Verify server IP geolocation fallback endpoint."""
        res = self.app.get('/api/my-location')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get('status'), 'success')
        self.assertIn('lat', data.get('location', {}))
        self.assertIn('lng', data.get('location', {}))

    def test_04_search_places(self):
        """Verify real place search autocomplete returns valid results."""
        res = self.app.get('/api/search-places?q=medicaps')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get('status'), 'success')
        self.assertGreater(data.get('count', 0), 0)
        names = [r['name'] for r in data.get('results', [])]
        self.assertTrue(any('Medi-Caps' in n for n in names))

    def test_05_institutions(self):
        """Verify prominent institutions catalog."""
        res = self.app.get('/api/institutions?lat=22.7196&lon=75.8577')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get('status'), 'success')
        self.assertGreater(len(data.get('institutions', [])), 5)

    def test_06_nearest_safe_places(self):
        """Verify nearest safe havens API endpoint."""
        res = self.app.get('/api/nearest-safe-places?lat=22.7196&lon=75.8577&limit=5')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get('status'), 'success')
        self.assertEqual(len(data.get('safe_places', [])), 5)
        first = data['safe_places'][0]
        self.assertIn('dist', first)
        self.assertIn('statusText', first)

    def test_07_sos_history(self):
        """Verify SOS history endpoint retrieves events."""
        res = self.app.get('/api/sos-history')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get('status'), 'success')
        self.assertIsInstance(data.get('events'), list)

    def test_08_voice_distress_detection(self):
        """Verify vocal distress keyword classifier."""
        res = self.app.post('/api/voice-status', json={'text': 'please help me bachao emergency'})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get('distress_detected'))

        # Safe sentence
        res2 = self.app.post('/api/voice-status', json={'text': 'hello good morning how are you'})
        self.assertEqual(res2.status_code, 200)
        data2 = res2.get_json()
        self.assertFalse(data2.get('distress_detected'))

    def test_09_send_alert_dry_run(self):
        """Verify SOS alert pipeline logs properly."""
        payload = {
            "type": "initial",
            "contacts": [
                {"name": "Emergency Test", "phone": "+919999999999"}
            ],
            "duration": 10,
            "timestamp": "2026-11-04T12:00:00Z",
            "location": "22.7196, 75.8577",
            "maps_link": "https://maps.google.com/?q=22.7196,75.8577"
        }
        res = self.app.post('/send-alert', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get('status'), 'success')
        self.assertIn('log_id', data)


if __name__ == '__main__':
    unittest.main()

