class BehaviorAdapter:
    def adjust_style(self, user_profile):
        if user_profile.get('extraversion', 0) > 0.7:
            return "high_interaction_mode"
        return "analytical_mode"
