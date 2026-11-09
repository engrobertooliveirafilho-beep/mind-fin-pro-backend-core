"""ET665.R46: historical MT5 ORDER_CHECK disabled; no terminal imports or calls."""

def run(symbol="EURUSD", lot=0.01):
    raise PermissionError("ET665_R27_MIRRORED_MT5_ORDER_CHECK_FORBIDDEN")


if __name__ == "__main__":
    run()
