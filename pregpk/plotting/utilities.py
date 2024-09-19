def row_and_col_subplot_positions(n_rows, n_cols, direction="horizontal"):

    if direction == "horizontal":
        rows = [i for i in range(1, n_rows+1) for _ in range(1, n_cols+1)]
        cols = [*range(1, n_cols+1)]*n_rows

    elif direction == "vertical":
        rows = [*range(1, n_rows+1)]*n_cols
        cols = [i for i in range(1, n_cols+1) for _ in range(1, n_rows+1)]

    else:
        raise ValueError("direction must be either 'horizontal' (default) or 'vertical'.")

    return rows, cols
