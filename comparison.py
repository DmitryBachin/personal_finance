import pandas as pd
from datetime import datetime

AMEX_COLUMNS = ("Date", "Reference", "Amount", "Note", "Datum verwerkt", "")
ING_COLUMNS_RENAME = {
    "Datum": "Date",
    "Bedrag (EUR)": "Amount",
    "Naam / Omschrijving": "Note",

}

COLUMNS_TO_KEEP = ("Date", "Amount", "Note",)


def change_date_format(date_string):
    if isinstance(date_string, int):
        date_string = str(date_string)
    date_object = datetime.strptime(date_string, "%Y%m%d")
    return date_object.strftime("%d/%m/%Y")


def universal_data_frame_change(data_frame, *columns_to_keep):
    if columns_to_keep:
        return data_frame[list(columns_to_keep)]

    return data_frame


def making_app_data_frame(file_path, *columns_to_keep):
    whole_data_frame = pd.read_csv(file_path, sep=";", decimal=",")
    return universal_data_frame_change(whole_data_frame, *columns_to_keep)


def making_amex_data_frame(file_path, *columns_to_keep):
    amex_data_frame = pd.read_csv(file_path, names=AMEX_COLUMNS, sep=';', decimal=",")
    return universal_data_frame_change(amex_data_frame, *columns_to_keep)


def making_ing_data_frame(file_path, *columns_to_keep):
    ing_data_frame = pd.read_csv(file_path, sep=';', decimal=",")
    ing_data_frame = ing_data_frame.rename(columns=ING_COLUMNS_RENAME)
    ing_data_frame["Date"] = ing_data_frame["Date"].apply(change_date_format)
    return universal_data_frame_change(ing_data_frame, *columns_to_keep)


def get_all_amounts(data_frame):
    amount_counter = {}
    all_amounts = list(data_frame["Amount"])
    for amount in all_amounts:
        if amount not in amount_counter:
            amount_counter[amount] = 0

        amount_counter[amount] += 1

    return amount_counter


def amount_comparison(bank_data_frame, app_data_frame):
    """

    :param bank_data_frame:
    :param app_data_frame:
    :return: amount count difference; positive - bank, negative - app
    """
    bank_amount_counter = get_all_amounts(bank_data_frame)
    app_amount_counter = get_all_amounts(app_data_frame)

    all_possible_amounts = {*bank_amount_counter.keys(), *app_amount_counter.keys()}

    different_amounts = {}
    for amount in all_possible_amounts:
        bank_amount_count = bank_amount_counter.get(amount, 0)
        app_amount_count = app_amount_counter.get(amount, 0)
        if bank_amount_count == app_amount_count:
            continue

        different_amounts[amount] = bank_amount_count - app_amount_count

    return {k: v for k, v in different_amounts.items() if v != 0}


def rows_extraction(data_frame, amounts):
    return data_frame[data_frame["Amount"].isin(amounts)]


def amount_search(bank_data_frame, app_data_frame):
    different_amounts = amount_comparison(bank_data_frame, app_data_frame)
    return rows_extraction(bank_data_frame, different_amounts), rows_extraction(app_data_frame, different_amounts)


if __name__ == "__main__":
    folder = "/Users/dmitrybachin/Documents/"

    file_paths = {
        "amex": "ofx.csv",
        "app": "mm.csv",
        "ing": "ing.csv",
    }

    data_frames = {}

    # getting data_frame with all data
    mm_df = making_app_data_frame(folder + file_paths["app"], "Date", "Account", "Amount", "Note")

    mm_accounts_df = mm_df[mm_df["Account"] == "Accounts"]
    mm_amex_df = mm_df[mm_df["Account"] == "AMEX FB card"]

    amex_df = making_amex_data_frame(folder + file_paths["amex"], *COLUMNS_TO_KEEP)
    ing_df = making_ing_data_frame(folder + file_paths["ing"], *COLUMNS_TO_KEEP)

    i, a = amount_search(ing_df, mm_accounts_df)
    print(i)
    print(a)
