import pytest
from app.mind.vector_pipeline import index_text, query_similar


def test_lexical_scope():
    index_text('gado leite', 'a', 's')
    index_text('motor diesel', 'a', 's')
    index_text('gado segredo', 'b', 's')
    assert query_similar('gado', 1, 'a', 's')[0]['text'] == 'gado leite'
    assert query_similar('gado', 5, 'a', 'other') == []
    assert len(query_similar('gado', 5, 'a', 's')) == 2


@pytest.mark.parametrize('text,user', [('', 'a'), ('gado', None), ('x'*16385, 'a')])
def test_invalid(text,user):
    with pytest.raises(ValueError):
        index_text(text,user,'s')
