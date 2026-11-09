"""ET665.R46: historical MT5 ORDER_CHECK disabled; no terminal imports or calls."""

def run(symbol="EURUSD", lot=0.01):
    raise PermissionError("ET665_MT5_UNCERTIFIED_ENTRYPOINT_BLOCKED")


if __name__ == "__main__":
    run()
