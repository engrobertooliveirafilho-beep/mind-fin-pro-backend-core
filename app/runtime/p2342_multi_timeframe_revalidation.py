from dataclasses import dataclass

@dataclass
class RevalidationResult:
    symbol:str
    side:str
    m1:bool
    m5:bool
    m15:bool
    h1:bool
    trend_filter:bool
    volatility_filter:bool
    session_filter:bool
    support_resistance_filter:bool

    def approved(self):
        score=sum([
            self.m1,
            self.m5,
            self.m15,
            self.h1,
            self.trend_filter,
            self.volatility_filter,
            self.session_filter,
            self.support_resistance_filter
        ])
        return score >= 7

def evaluate(symbol,side,context):
    return RevalidationResult(
        symbol=symbol,
        side=side,
        m1=context.get("m1",False),
        m5=context.get("m5",False),
        m15=context.get("m15",False),
        h1=context.get("h1",False),
        trend_filter=context.get("trend_filter",False),
        volatility_filter=context.get("volatility_filter",False),
        session_filter=context.get("session_filter",False),
        support_resistance_filter=context.get("support_resistance_filter",False)
    )
