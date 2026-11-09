"""ET665.R48: uncertified MT5 access disabled before import and terminal access."""

def run():
    raise PermissionError("ET665_MT5_UNCERTIFIED_ENTRYPOINT_BLOCKED")


if __name__ == "__main__":
    run()
