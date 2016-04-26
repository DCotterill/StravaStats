from stravalib import model as model

__author__ = 'darren'


class ActivityConverter(model.Activity):
    stravaActivity = model.Activity;

    def convertToFitBit(self):
        fitbitActivity = FitbitActivity()
        fitbitActivity.distance = self.stravaActivity.distance

        return fitbitActivity

class FitbitActivity():
    distance = 0

