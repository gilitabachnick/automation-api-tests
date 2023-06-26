from enum import Enum
#from selectors import PollSelector


class AnalyticsMenuTabs(Enum):
    # def __str__(self):
    #     return str(self.value)

    AUDIENCE         = 'AUDIENCE'
    CONTRIBUTORS     = 'CONTRIBUTORS'
    USAGE            = 'USAGE'
    REAL_TIME        = 'REAL-TIME'


class AnalyticsSubMenuTabs(Enum):
    def __str__(self):
        return str(self.value)

    ENGAGEMENT              = 'ENGAGEMENT'
    CONTENT_INTERACTIONS    = 'CONTENT INTERACTIONS'
    TECHNOLOGY              = 'TECHNOLOGY'
    GEO_LOCATION            = 'GEO LOCATION'

class SectionTitles(Enum):
    def __str__(self):
        return str(self.value)

    HIGHLIGHTS              = 'Highlights'
    TOP_VIDEOS              = 'Top Videos'
    INSIGHTS                = 'Insights'

class ReportsTabsNames(Enum):
    def __str__(self):
        return str(self.value)

    PLAYER_IMPRESSIONS        = 'Player Impressions'
    PLAYS                     = 'Plays'
    UNIQUE_VIEWERS            = 'Unique Viewers'
    MINUTES_VIEWED            = 'Minutes Viewed'
    AVG_DROP_OFF_RATE         = 'Avg. Drop Off Rate'
    AVG_MIN_VIEWED            = 'Avg. Min Viewed'
    SHARES                    = 'Shares'
    DOWNLOADS                 = 'Downloads'
    ABUSE_REPORT              = 'Abuse Report'
    ADDED_ENTRIES             = 'Added Entries'
    ADDED_MINUTES             = 'Added Minutes'
    CONTRIBUTORS              = 'Contributors'
    

class PagerNav(Enum):
    def __str__(self):
        return str(self.value)

    NEXT        = 'next'
    PREV        = 'prev'
    LAST        = 'last'
    FIRST       = 'first'
    PAGE        = 'page'
