import pandas as pd


def new_cols_params(selected_cols_number, sports_book_count):
    new_cols_params_dict = {}

    # sports_book_name_xxx and the index range
    start_cols_index = selected_cols_number
    end_cols_index = start_cols_index + sports_book_count
    new_cols_params_dict['sports_book_name_'] = (start_cols_index, end_cols_index)

    # odd_xxx and the index range
    start_cols_index = end_cols_index
    end_cols_index = start_cols_index + sports_book_count
    new_cols_params_dict['odd_'] = (start_cols_index, end_cols_index)

    # hedge_book_xxx and the index range
    start_cols_index = end_cols_index
    end_cols_index = start_cols_index + sports_book_count
    new_cols_params_dict['hedge_book_'] = (start_cols_index, end_cols_index)

    # hedge_odd_xxx and the index range
    start_cols_index = end_cols_index
    end_cols_index = start_cols_index + sports_book_count
    new_cols_params_dict['hedge_odd_'] = (start_cols_index, end_cols_index)

    return new_cols_params_dict


def cols_index(col_name, new_cols_params_dict):
    start = new_cols_params_dict[col_name][0]
    end = new_cols_params_dict[col_name][1]
    return start, end


def create_2side(selected_cols_list, new_cols_params_dict):
    all_cols_list = list(selected_cols_list)
    for key in new_cols_params_dict:
        start, end = cols_index(key, new_cols_params_dict)
        new_cols_list = [key + str(i + 1) for i in range(end - start)]
        all_cols_list.extend(new_cols_list)
    df_out = pd.DataFrame(columns=all_cols_list)
    return df_out


def update_sports_book(df_2side, row_index, col_index, sports_book_name, price, sports_book_count):
    # Sports book data
    df_2side.iloc[row_index, col_index] = sports_book_name
    col_index += sports_book_count
    df_2side.iloc[row_index, col_index] = price


def convert_to_2sides(df_1side, df_2side, selected_cols_number, sports_book_count):
    keys_dict = {}
    cols_list_2side = df_2side.columns.tolist()

    i = 0
    # Visit all row of the 1-sided table
    for idx, row_1side in df_1side.iterrows():
        i += 1

        # Get the essential column values in the current row of 1-sided table and determine the primary key
        sports_book_name = row_1side['sports_book_name']
        name = row_1side['name']
        price = row_1side['price']
        market_name = row_1side['market_name']
        key = name + market_name

        # Insert data of the selected columns into the 2-sided table if its 'name' does not exist
        # And find the column position to update data
        if key not in keys_dict:
            col_index = selected_cols_number
            # insert a new row to 2-sided table with the essential values
            row_2side = create_2side_row(row_1side, cols_list_2side)
            df_2side.loc[len(df_2side.index)] = row_2side
        else:
            col_index = keys_dict[key] + 1
        keys_dict.update({key: col_index})

        # find the row position to update data
        row_index = find_row_index(df_2side, name, market_name)

        # Update sport book data to 2-sided table
        update_sports_book(df_2side, row_index, col_index, sports_book_name, price, sports_book_count)

        if i % 500 == 0:
            print(". ", end='')


def create_2side_row(row_1side, cols_list_2side):
    row_2side = []
    for col_name in cols_list_2side:
        if col_name in row_1side:
            # add data to the selected columns
            row_2side.append(row_1side[col_name])
        else:
            # add blank to all new columns
            row_2side.append('')
    return row_2side


def update_hedge_book(df_2side, new_cols_params_dict):
    for row_index in range(len(df_2side.index)):
        market_name = df_2side['market_name'][row_index]
        name = df_2side['name'][row_index]

        # Moneyline
        if 'Moneyline' in market_name:

            # find the other name
            game_home_team = df_2side['game_home_team'][row_index]
            game_away_team = df_2side['game_away_team'][row_index]
            if name == game_home_team:
                other_name = game_away_team
            else:
                other_name = game_home_team

            # Update hedge data
            update_hedge(df_2side, row_index, other_name, market_name, new_cols_params_dict)

        # Over vs Under
        if 'Over' in name:
            # find the other name
            other_name = name.replace('Over', 'Under')

            # Update hedge data
            update_hedge(df_2side, row_index, other_name, market_name, new_cols_params_dict)

        # Spread
        if 'Spread' in market_name:
            # find the other name
            game_home_team = df_2side['game_home_team'][row_index]
            game_away_team = df_2side['game_away_team'][row_index]
            bet_points = df_2side['bet_points'][row_index]
            other_bet_points = -bet_points
            s_bet_points = sign(bet_points) + str(bet_points)
            s_other_bet_points = sign(other_bet_points) + str(other_bet_points)

            if game_home_team in name:
                other_name = name.replace(game_home_team + ' ' + s_bet_points,
                                          game_away_team + ' ' + s_other_bet_points)
            else:
                other_name = name.replace(game_away_team + ' ' + s_bet_points,
                                          game_home_team + ' ' + s_other_bet_points)

            # Update hedge data
            update_hedge(df_2side, row_index, other_name, market_name, new_cols_params_dict)


def update_hedge(df_2side, row_index, other_name, market_name, new_cols_params_dict):

    # find row index of the other name
    row_index_other = find_row_index(df_2side, other_name, market_name)
    if row_index_other == -1:
        return
    row_data = df_2side.iloc[row_index]
    row_data_other = df_2side.iloc[row_index_other]

   # hedge_book_
    # Start column index of sports_book_name_ and "hedge_book_"
    start0, end0 = cols_index("sports_book_name_", new_cols_params_dict)
    start, end = cols_index("hedge_book_", new_cols_params_dict)
    for i in range(end - start):
        df_2side.iloc[row_index, start + i] = row_data_other[start0 + i]
        df_2side.iloc[row_index_other, start + i] = row_data[start0 + i]

    # Hedge_odd_
    # Start column index of odd_ and "hedge_odd_"
    start0, end0 = cols_index("odd_", new_cols_params_dict)
    start, end = cols_index("hedge_odd_", new_cols_params_dict)
    for i in range(end - start):
        df_2side.iloc[row_index, start + i] = row_data_other[start0 + i]
        df_2side.iloc[row_index_other, start + i] = row_data[start0 + i]


def sign(number):
    s = ''
    if number > 0:
        s = '+'
    return s


def find_row_index(df_2side, name, market_name):
    try:
        index = df_2side.index[(df_2side['name'] == name) & (df_2side['market_name'] == market_name)].tolist()[0]
    except IndexError:
        index = -1
    return index


def main_prg(csv_name):
    print("Preparing data")
    # convert data from cvs file to dataframe (table)
    data = pd.read_csv(csv_name)
    df_1side = pd.DataFrame(data)
    df_1side.fillna('', inplace=True)

    # Select a list of columns with a new order from the 1-side table
    selected_cols_list = ['name', 'market_name', 'bet_points', 'is_main', 'is_live',
                          'home_rotation_number', 'away_rotation_number', 'deep_link_url',
                          'player_id', 'game_id', 'game_sport', 'game_league', 'game_start_date',
                          'game_home_team', 'game_away_team', 'game_is_live']
    selected_cols_number = len(selected_cols_list)

    # count the number of sports book
    sports_book_count = df_1side['sports_book_name'].nunique()

    # Calculate the parameters for the 2-sided table columns (column names and column indexes)
    new_cols_params_dict = new_cols_params(selected_cols_number, sports_book_count)

    # Create an empty 2-side table with selected columns and extended columns
    df_2side = create_2side(selected_cols_list, new_cols_params_dict)

    # Initialize 2-sided table data from 1-sided table data
    print('Convert and update data')
    convert_to_2sides(df_1side, df_2side, selected_cols_number, sports_book_count)

    # Update hedge book data
    update_hedge_book(df_2side, new_cols_params_dict)

    # Export 2-sided table to csv file
    print()
    print('Export the result to superbowl_2s.csv')
    df_2side.to_csv('superbowl_2s.csv')


if __name__ == '__main__':
    main_prg('superbowl_all.csv')
