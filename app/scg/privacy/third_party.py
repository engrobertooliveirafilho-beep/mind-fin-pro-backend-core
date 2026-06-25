class ThirdPartyProtection:
    def filter(self, input_data):
        return {
            "contains_third_party": False,
            "analysis_allowed": True
        }
