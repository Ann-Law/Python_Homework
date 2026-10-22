"""
Unit tests for Problem 4: MeetingRoom

Instructions:
Complete the unit test methods below using Python's unittest framework.
Your test methods must assert MULTIPLE ATTRIBUTES on the MeetingRoom object
(e.g., bookings list, total_hours_booked, free slots, utilization rate)
to verify room state and conflict management.

Running tests:
    python -m unittest test_problem4.py -v
"""
import unittest
from problem4 import MeetingRoom


class TestMeetingRoom(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.room = MeetingRoom("Conference-A", capacity=10)

    def test_initial_state_multi_attributes(self):
        """
        Verify initial state of an empty meeting room.
        """
        self.assertEqual(self.room.room_id, "Conference-A")
        self.assertEqual(self.room.capacity, 10)
        self.assertEqual(len(self.room.bookings), 0)
        self.assertEqual(self.room.total_hours_booked, 0)
        self.assertFalse(self.room.is_maintenance)
        # Whole day 8-18 should be free
        self.assertEqual(self.room.get_free_slots(), [(8, 18)])
        self.assertEqual(self.room.get_utilization_rate(), 0.0)

    def test_single_booking_multi_attributes(self):
        """
        Test making a single valid booking.
        Verify bookings list, total_hours_booked, utilization rate, and free slots.
        """
        # TODO: Book meeting 'B01' from 10 to 12 with 5 attendees
        # Book meeting 'B01' from 10 to 12 with 5 attendees
        result = self.room.book("B01", "Team Sync", 10, 12, attendees=5)

        self.assertTrue(result)
        self.assertEqual(len(self.room.bookings), 1)
        self.assertEqual(self.room.bookings[0]["booking_id"], "B01")
        self.assertEqual(self.room.bookings[0]["start_time"], 10)
        self.assertEqual(self.room.bookings[0]["end_time"], 12)
        self.assertEqual(self.room.bookings[0]["attendees"], 5)
        # 12 - 10 = 2 hours booked
        self.assertEqual(self.room.total_hours_booked, 2)
        # utilization = 2 / 10 = 0.2
        self.assertEqual(self.room.get_utilization_rate(), 0.2)
        # Free slots: (8,10) and (12,18)
        self.assertEqual(self.room.get_free_slots(), [(8, 10), (12, 18)])

    def test_back_to_back_meetings_allowed(self):
        """
        Test that valid consecutive / back-to-back meetings (e.g. 9-10 and 10-12)
        are permitted without raising conflict errors.
        Verify multi-attribute state after both bookings succeed.
        """
        # TODO: Book 'B01' from 9 to 10
        # Book B01 from 9 to 10
        self.room.book("B01", "Standup", 9, 10, attendees=4)
        # Book B02 from 10 to 12 (back-to-back, should NOT conflict)
        self.room.book("B02", "Sprint Planning", 10, 12, attendees=6)

        self.assertEqual(len(self.room.bookings), 2)
        # 1 hour + 2 hours = 3 hours
        self.assertEqual(self.room.total_hours_booked, 3)
        self.assertEqual(self.room.get_utilization_rate(), 0.3)
        # Free slots: (8,9) and (12,18)
        self.assertEqual(self.room.get_free_slots(), [(8, 9), (12, 18)])

    def test_overlapping_booking_rejected(self):
        """
        Test that overlapping bookings (e.g. 9-11 and 10-12, or completely inside 9-12 and 10-11)
        raise ValueError and leave room state unchanged.
        """
        # TODO: Implement test with self.assertRaises(ValueError)
        # Book B01 from 9 to 12
        self.room.book("B01", "Long Meeting", 9, 12, attendees=5)

        # Try to book B02 from 10 to 11 (completely inside 9-12) → conflict
        with self.assertRaises(ValueError):
            self.room.book("B02", "Overlap Inside", 10, 11, attendees=3)

        # Try to book B03 from 11 to 13 (overlaps 11-12) → conflict
        with self.assertRaises(ValueError):
            self.room.book("B03", "Overlap End", 11, 13, attendees=3)

        # Room state should be unchanged: still only 1 booking, 3 hours
        self.assertEqual(len(self.room.bookings), 1)
        self.assertEqual(self.room.total_hours_booked, 3)

    def test_cancel_booking_updates_all_attributes(self):
        """
        Test that cancelling a booking correctly removes it from bookings,
        decrements total_hours_booked, and restores free slots.
        """
        # TODO: Book two meetings, cancel one, verify all attributes
        # Book two meetings
        self.room.book("B01", "Morning", 9, 11, attendees=4)   # 2 hours
        self.room.book("B02", "Afternoon", 13, 15, attendees=6)  # 2 hours
        self.assertEqual(self.room.total_hours_booked, 4)
        self.assertEqual(len(self.room.bookings), 2)

        # Cancel B01
        result = self.room.cancel("B01")
        self.assertTrue(result)
        # Only B02 remains (2 hours)
        self.assertEqual(len(self.room.bookings), 1)
        self.assertEqual(self.room.bookings[0]["booking_id"], "B02")
        self.assertEqual(self.room.total_hours_booked, 2)
        self.assertEqual(self.room.get_utilization_rate(), 0.2)
        # Free slots: (8,13) and (15,18)
        self.assertEqual(self.room.get_free_slots(), [(8, 13), (15, 18)])

    def test_capacity_and_validation_exceptions(self):
        """
        Test edge cases and exceptions:
        - Attendees exceeding capacity (ValueError)
        - Start time >= End time (ValueError)
        - Duplicate booking ID (ValueError)
        - Booking when room is under maintenance (RuntimeError)
        - Cancelling non-existent booking (KeyError)
        """
        # TODO: Implement exception tests using self.assertRaises()
        # Attendees exceeding capacity (capacity=10)
        with self.assertRaises(ValueError):
            self.room.book("B01", "Big", 9, 10, attendees=11)

        # End time <= start time
        with self.assertRaises(ValueError):
            self.room.book("B02", "Bad", 10, 10, attendees=5)  # end == start
        with self.assertRaises(ValueError):
            self.room.book("B03", "Worse", 10, 9, attendees=5)  # end < start

        # Duplicate booking ID
        self.room.book("B04", "First", 9, 10, attendees=5)
        with self.assertRaises(ValueError):
            self.room.book("B04", "Duplicate", 14, 15, attendees=5)

        # Booking when room is under maintenance
        self.room.is_maintenance = True
        with self.assertRaises(RuntimeError):
            self.room.book("B05", "No", 9, 10, attendees=5)
        self.room.is_maintenance = False  # reset

        # Cancelling non-existent booking → KeyError
        with self.assertRaises(KeyError):
            self.room.cancel("B999")

if __name__ == "__main__":
    unittest.main()
