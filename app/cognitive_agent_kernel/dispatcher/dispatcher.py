class ExecutionDispatcher:
    def dispatch(self, plan):
        """Classify plans without claiming execution or authorizing side effects."""
        if not isinstance(plan, dict):
            raise ValueError('Invalid plan')
        if plan.get('status') == 'PLANNED':
            return 'AWAITING_AUTHORIZATION'
        return 'QUEUED'
