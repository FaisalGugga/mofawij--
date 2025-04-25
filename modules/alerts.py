class AlertSystem:
    def check_congestion(self, people_count):
        if people_count > 15:
            return "Alert: Almost Full - Notify Security,", "Take Control"
        elif people_count > 9:
            return "Warning: Getting Crowded,"," Keep it Open"
        else:
            return "No congestion,"," Keep it Open"