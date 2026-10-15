def test_pandas_dataframe():
    import pandas

    assert len(pandas.DataFrame({"a": [1, 2]})) == 2
