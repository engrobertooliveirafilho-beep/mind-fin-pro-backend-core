"""ET665.R48: uncertified MT5 access disabled before import and terminal access."""

def check(symbol="EURUSD", lot=0.01):
    raise PermissionError("ET665_MT5_UNCERTIFIED_ENTRYPOINT_BLOCKED")


if __name__ == "__main__":
    check()
