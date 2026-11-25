from app.ethical_review import EthicalReviewBoard


def test_step542_submit_creates_pending_item_and_lists_pending():
    board = EthicalReviewBoard()
    item = board.submit({"decision": "aprovar_emprestimo", "risk": "alto"})
    pending = board.list_pending()

    assert item.item_id.startswith("ERB-")
    assert item.status == "pending"
    assert len(pending) == 1
    assert pending[0].item_id == item.item_id


def test_step542_approve_moves_item_out_of_pending_and_sets_reviewer():
    board = EthicalReviewBoard()
    item = board.submit({"decision": "bloquear_conta", "risk": "muito_alto"})
    board.approve(item.item_id, reviewer="ethics_officer", notes="Conforme politica X.")

    pending = board.list_pending()
    assert len(pending) == 0

    stored = board._items[item.item_id]
    assert stored.status == "approved"
    assert stored.reviewer == "ethics_officer"
    assert stored.reviewed_at is not None

