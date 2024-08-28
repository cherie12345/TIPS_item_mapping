import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import re
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
plt.rcParams['font.family'] ='Malgun Gothic'
plt.rcParams['axes.unicode_minus'] =False
from collections import Counter

def test():
    print('working!')
    return 
# ==================================================================== Data Structure Transformation 

def split_text_to_words(row):
    """
    Helper function to be used with apply. Splits the text in a row into words.

    Parameters:
    - row (pd.Series): A row in the DataFrame.

    Returns:
    - list: A list of words from the text in the row.
    """
    text = str(row)
    words = text.split()
    return words


def split_text_column_to_words(dataframe, column_name):
    """
    Takes a DataFrame and a column containing text, splits the text into words using the apply function, 
    and returns a list of words for each row in the specified column.

    Parameters:
    - dataframe (pd.DataFrame): The DataFrame containing the text column.
    - column_name (str): The name of the column containing text.

    Returns:
    - list of lists: A list of lists where each sublist contains words from the corresponding row.
    """
    if column_name not in dataframe.columns:
        raise ValueError(f"Column '{column_name}' not found in the DataFrame.")

    words_list = dataframe[column_name].apply(split_text_to_words).tolist()

    return words_list


def flatten_once(nested_list):
    return [item for sublist in nested_list for item in (sublist if isinstance(sublist, list) else [sublist])]





# ==================================================================== Text / noise Preprocessing 

def strip_special_characters(string):
    # Define a regular expression pattern to match leading and trailing spaces and special characters
    pattern = r'^[\s\W_]+|[\s\W_]+$'
    
    # Use re.sub to replace matching patterns with an empty string
    stripped_string = re.sub(pattern, '', string)
    
    return stripped_string


def sort_item_name(df):

    # Drop duplicates based on all columns
    new_df = df.drop('price', axis=1)
    new_df = new_df.drop_duplicates()

    # Calculate text length and sort by 'text_length'
    new_df['text_length'] = new_df['productTitle'].apply(len)
    sorted_df = new_df.sort_values(by='text_length')

    # Drop the temporary 'text_length' column if not needed
    sorted_df = sorted_df.drop(columns='text_length')

    return sorted_df


def select_brand(df, brand_name):
    # Filter DataFrame for the given brand
    new_df = df[df['brand'] == brand_name]

    # Drop duplicates based on all columns
    new_df = new_df.drop('price', axis=1)
    new_df = new_df.drop_duplicates()

    # Calculate text length and sort by 'text_length'
    new_df['text_length'] = new_df['productTitle'].apply(len)
    sorted_df = new_df.sort_values(by='text_length')

    # Drop the temporary 'text_length' column if not needed
    sorted_df = sorted_df.drop(columns='text_length')

    return sorted_df


def filter_brands(nested_list, target_word):
    filtered_list = []

    for inner_list in nested_list:
        filtered_inner_list = [word for word in inner_list if word != target_word]
        filtered_list.append(filtered_inner_list)

    return filtered_list


def filter_words(nested_list, target_words):
    filtered_list = []

    for inner_list in nested_list:
        filtered_inner_list = inner_list.copy()  # Create a copy to avoid modifying the original list
        for target_word in target_words:
            if target_word != '':
                filtered_inner_list = [word for word in filtered_inner_list if str(target_word) not in str(word)]
        filtered_list.append(filtered_inner_list)

    return filtered_list


def drop_cols_n_sort_itname(df):
    '''
    drop price columns and drop duplicates 
    return sorted unique items 
    '''

    # Drop duplicates based on all columns
    new_df = df.drop('price', axis=1)
    new_df = new_df.drop_duplicates()

    # Calculate text length and sort by 'text_length'
    new_df['text_length'] = new_df['productTitle'].apply(len)
    sorted_df = new_df.sort_values(by='text_length')

    # Drop the temporary 'text_length' column if not needed
    sorted_df = sorted_df.drop(columns='text_length')

    return sorted_df


def filter_words_with_numeric(words_list):
    filtered_list = [word for word in words_list if any(char.isdigit() for char in word)]
    return filtered_list


def filter_words_with_numeric_and_g(words_list):
    filtered_list = [word for word in words_list if any(char.isdigit() for char in word) and 'g' in word.lower()]
    return filtered_list


# ==================================================================== Visualization / Overview


'''
def plot_word_histogram(nested_list):
    # Flatten the nested list
    flat_list = [word for sublist in nested_list for word in sublist]

    # Count the frequency of each word
    word_counts = Counter(flat_list)

    # Sort words and frequencies in descending order
    sorted_word_counts = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    print(sorted_word_counts)
    words, frequencies = zip(*sorted_word_counts)

    # Plot the word histogram
    plt.figure(figsize=(6, 4))
    plt.bar(words, frequencies, color='blue')
    plt.xlabel('Words')
    plt.ylabel('Frequency')
    plt.title('Word Histogram')
    plt.xticks(rotation=45, ha='right')
    plt.show()

    return sorted_word_counts
'''

def plot_word_histogram(sorted_word_counts):
    words, frequencies = zip(*sorted_word_counts)
    words = [str(word) for word in words]

    # Plot the word histogram
    plt.figure(figsize=(15, 4))
    plt.bar(words, frequencies, color='orange')
    plt.xlabel('Words')
    plt.ylabel('Frequency')
    plt.title('Word Histogram')
    plt.xticks(rotation=45, ha='right')
    plt.show()

    return sorted_word_counts

def word_counts(nested_list): 
    # Flatten the nested list
    flat_list = [word for sublist in nested_list for word in sublist]

    # Count the frequency of each word
    word_counts = Counter(flat_list)

    # Sort words and frequencies in descending order
    sorted_word_counts = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)

    return sorted_word_counts



# ==================================================================== Compute Mapping
def select_names_with_same_group(df, given_name):
    given_group = df.loc[df['name'] == given_name, 'group'].iloc[0]
    names_same_group = df.loc[df['group'] == given_group, 'name'].tolist()
    df['actual'] = df['group'].apply(lambda x: 'T' if x == given_group else 'F')
    return names_same_group, df



# ==================================================================== Evaluation 

def compute_metrics(predicted, actual):
    true_positive = sum(p == a == 'T' for p, a in zip(predicted, actual))
    true_negative = sum(p == a == 'F' for p, a in zip(predicted, actual))
    false_positive = sum(p == 'T' and a == 'F' for p, a in zip(predicted, actual))
    false_negative = sum(p == 'F' and a == 'T' for p, a in zip(predicted, actual))
    
    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive != 0 else 0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative != 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if precision + recall != 0 else 0
    accuracy = (true_positive + true_negative) / len(predicted) if len(predicted) != 0 else 0
    
    return round(precision, 2), round(recall, 2), round(f1_score, 2), round(accuracy, 2)