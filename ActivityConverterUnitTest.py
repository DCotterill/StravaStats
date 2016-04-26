from ActivityConverter import ActivityConverter

import unittest

import stravalib.model as model

class ActivityConverterUnitTestCase(unittest.TestCase):
    def test_create_simple_fitbit_activity_from_strava(self):
        stravaActivity = model.Activity()
        stravaActivity.distance = "12.6"
        activityConverter = ActivityConverter(stravaActivity)

        fitbitActivity = activityConverter.convertToFitBit()
        self.assertEqual(fitbitActivity.distance, stravaActivity.distance)


if __name__ == '__main__':
    unittest.main()
