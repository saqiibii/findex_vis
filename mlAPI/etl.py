import pandas as pd
import numpy as np
import os

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import MinMaxScaler

import time
from config import *
import plots as plots

# from config import *
# import data_plots
import pickle
 
import pandas as pd
from datetime import datetime
import numpy as np
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.cluster import DBSCAN
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import SpectralClustering
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

def handle_null_and_transform_old(df,label_encoders=None):
    """
    Handles null values in the dataframe and applies transformations based on the specified rules.
    
    Args:
        df (pd.DataFrame): The input dataframe.
    
    Returns:
        pd.DataFrame: The transformed dataframe.
        dict: A dictionary containing label encoders for categorical columns.
    """
    print("herro")
    if label_encoders is None:
        label_encoders = {}
    scaler = MinMaxScaler()  # For normalization
    df['Age'] = df['Age'].fillna(0).astype(int)
    df['Age Group'] = pd.cut(
        df['Age'], bins=[-1, 12, 19, 35, 50, 65, np.inf],
        labels=[0, 1, 2, 3, 4, 5])
    df['Age Group'] = df['Age Group'].astype(int)
    df['Annual Income'] = df['Annual Income'].fillna(0)
    df['Annual Income'] = np.log10(df['Annual Income'] + 1)  # Adding 1 to avoid log(0)
    df['Marital Status'] = df['Marital Status'].fillna("unknown")
    
    if 'Marital Status' in label_encoders:
        df['Marital Status'] = label_encoders['Marital Status'].transform(df['Marital Status'])
    else:
        le_marital_status = LabelEncoder()
        df['Marital Status'] = le_marital_status.fit_transform(df['Marital Status'])
        label_encoders['Marital Status'] = le_marital_status
    print("check2")

    if 'Number of Dependents' in label_encoders:
        df['Number of Dependents'] = label_encoders['Number of Dependents'].transform(df['Number of Dependents'])
    else:
        le_depend = LabelEncoder()
        df['Number of Dependents'] = le_depend.fit_transform(df['Number of Dependents'])
        label_encoders['Number of Dependents'] = le_depend
    print("check3")

    df['Occupation'] = df['Occupation'].fillna("unknown")
    print("check4")
    if 'Occupation' in label_encoders:
        df['Occupation'] = label_encoders['Occupation'].transform(df['Occupation'])
    else:
        le_occupation = LabelEncoder()
        df['Occupation'] = le_occupation.fit_transform(df['Occupation'])
        label_encoders['Occupation'] = le_occupation

    
    df['Health Score'] = df['Health Score'].fillna(-1)
    df['Health Score'] = scaler.fit_transform(df[['Health Score']])
    df['Previous Claims'] = df['Previous Claims'].fillna(0)
    df['Vehicle Age'] = df['Vehicle Age'].fillna(0)
    df['Credit Score'] = df['Credit Score'].fillna(df['Credit Score'].mean())
    df['Insurance Duration'] = df['Insurance Duration'].fillna(0)
    df['Customer Feedback'] = df['Customer Feedback'].fillna("unknown")
    if 'Customer Feedback' in label_encoders:
        df['Customer Feedback'] = label_encoders['Customer Feedback'].transform(df['Customer Feedback'])
    else:
        le_feedback = LabelEncoder()
        df['Customer Feedback'] = le_feedback.fit_transform(df['Customer Feedback'])
        label_encoders['Customer Feedback'] = le_feedback

    categorical_columns = [
       'Gender', 'Education Level', 
        'Location', 'Policy Type', 'Smoking Status', 
        'Exercise Frequency', 'Property Type'
    ]
    for col in categorical_columns:
        if label_encoders and col in label_encoders:
            df[col] = label_encoders[col].transform(df[col])
        else:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col])  # Overwrite the original column with encoded values
            label_encoders[col] = le   # Save the encoder for future use

    return df, label_encoders


def handle_null_and_transform(df,label_encoders=None):
    """
    Handles null values in the dataframe and applies transformations based on the specified rules.
    
    Args:
        df (pd.DataFrame): The input dataframe.
    
    Returns:
        pd.DataFrame: The transformed dataframe.
        dict: A dictionary containing label encoders for categorical columns.
    """
    if label_encoders is None:
        label_encoders = {}
    print("here")
    scaler = MinMaxScaler()  # For normalization
    df['Age'] = df['Age'].fillna(-1).astype(int)
    df['Age Group'] = pd.cut(
        df['Age'], bins=[-2,0, 12, 19, 35, 50, 65, np.inf],
        labels=[0, 1, 2, 3, 4, 5,6])
    print("here")
    df['Age Group'] = df['Age Group'].astype(int)
    print("here")
    df['Annual Income'] = df['Annual Income'].fillna(0)
    print("here")
    df['Annual Income'] = np.log10(df['Annual Income'] + 1)  # Adding 1 to avoid log(0)
    print("here1")
    df['Marital Status'] = df['Marital Status'].fillna("unknown")
    if 'Marital Status' in label_encoders:
        df['Marital Status'] = label_encoders['Marital Status'].transform(df['Marital Status'])
    else:
        le_marital_status = LabelEncoder()
        df['Marital Status'] = le_marital_status.fit_transform(df['Marital Status'])
        label_encoders['Marital Status'] = le_marital_status
    print("here2")
    if 'Number of Dependents' in label_encoders:
        df['Number of Dependents'] = label_encoders['Number of Dependents'].transform(df['Number of Dependents'])
    else:
        le_depend = LabelEncoder()
        df['Number of Dependents'] = le_depend.fit_transform(df['Number of Dependents'])
        label_encoders['Number of Dependents'] = le_depend
    print("here3")
    df['Occupation'] = df['Occupation'].fillna("unknown")
    if 'Occupation' in label_encoders:
        df['Occupation'] = label_encoders['Occupation'].transform(df['Occupation'])
    else:
        le_occupation = LabelEncoder()
        df['Occupation'] = le_occupation.fit_transform(df['Occupation'])
        label_encoders['Occupation'] = le_occupation
    print("here4")
    
    df['Health Score'] = df['Health Score'].fillna(-1)
    df['Health Score'] = scaler.fit_transform(df[['Health Score']])
    df['Previous Claims'] = df['Previous Claims'].fillna(-1)
    df['Vehicle Age'] = df['Vehicle Age'].fillna(-1)
    df['Credit Score'] = df['Credit Score'].fillna(-1)
    df['Insurance Duration'] = df['Insurance Duration'].fillna(-1)
    df['Customer Feedback'] = df['Customer Feedback'].fillna("unknown")
    if 'Customer Feedback' in label_encoders:
        df['Customer Feedback'] = label_encoders['Customer Feedback'].transform(df['Customer Feedback'])
    else:
        le_feedback = LabelEncoder()
        df['Customer Feedback'] = le_feedback.fit_transform(df['Customer Feedback'])
        label_encoders['Customer Feedback'] = le_feedback

    categorical_columns = [
       'Gender', 'Education Level', 
        'Location', 'Policy Type', 'Smoking Status', 
        'Exercise Frequency', 'Property Type'
    ]
    for col in categorical_columns:
        if label_encoders and col in label_encoders:
            df[col] = label_encoders[col].transform(df[col])
        else:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col])  # Overwrite the original column with encoded values
            label_encoders[col] = le   # Save the encoder for future use

    return df, label_encoders

def convert_and_normalize_days_since_policy_start(df, date_column):
    df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
    today = datetime.today()
    df['days_since_policy_start'] = (today - df[date_column]).dt.days
    df['days_since_policy_start'] = df['days_since_policy_start'].apply(lambda x: max(x, 1) if pd.notnull(x) else np.nan)
    df['log_days_since_policy_start'] = np.log10(df['days_since_policy_start'])
    df.drop(columns=[date_column], inplace=True)
    return df

def get_categorical_columns(df, unique_threshold=30):
    categorical_columns = []
    for col in df.columns:
        unique_values = df[col].nunique()
        if df[col].dtype == 'object' or unique_values <= unique_threshold:
            categorical_columns.append(col)
    print(f"Identified categorical columns: {categorical_columns}")
    return categorical_columns

def encode_and_save_labels(df, categorical_columns):
    label_encoders = {}
    for col in categorical_columns:
        if col in df.columns:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))  # Ensure all values are strings
            label_encoders[col] = le
    encoder_path = f"{LABEL_ENCODERS_PKL_OUTDIR}/lencoders.pkl"
    with open(encoder_path, "wb") as f:
        pickle.dump(label_encoders, f)
    print(f"Label encoders saved at {encoder_path}")
    return df

def do_ul_cluster(X_df):
    target_col = X_df[TARGET_COL]
    X_og = X_df.drop(columns=[TARGET_COL]) 

    print("kmeans")
    kmeans = KMeans(n_clusters=UL_CLUSTER_COUNT, random_state=GT_ID)
    km_clus = kmeans.fit_predict(X_og)
    X_df['km_clus'] = km_clus

    print("gmm")
    gmm = GaussianMixture(n_components=UL_CLUSTER_COUNT, random_state=GT_ID)
    gmm_clus = gmm.fit_predict(X_og)
    X_df['gmm_clus'] = gmm_clus

    # print("dbscan")
    # dbscan = DBSCAN(eps=1.0, min_samples=3)
    # dbscan_clus = dbscan.fit_predict(X_og)
    # X_df['dbscan_clus'] = dbscan_clus
    
    # print("spec clus")
    # spectral = SpectralClustering(n_clusters=ul_cluster_count, affinity='nearest_neighbors', random_state=GT_ID)
    # spectral_clus = spectral.fit_predict(X_og)
    # X_df['spectral_clus'] = spectral_clus

    X_df[TARGET_COL] = target_col

    return X_df

def get_data():
    print(f"Getting data for {DATASET_SELECTION}")
    if "findex" in DATASET_SELECTION:
        print(PROCESSED_TRAIN_PATH)
        if not os.path.exists(PROCESSED_TRAIN_PATH):
            try:
                df = pd.read_csv(TRAIN_PATH, encoding="ISO-8859-1")
                print("Accessed .csv in data folder")

                available_columns = [col for col in COLUMNS_TO_KEEP + [TARGET_COL] if col in df.columns]
                df = df[available_columns]
                df = df.loc[:, ~df.columns.duplicated()]

                # df = df[COLUMNS_TO_KEEP+[TARGET_COL] if TARGET_COL not in COLUMNS_TO_KEEP else COLUMNS_TO_KEEP ]
                economy_column = df[['economy', 'pop_adult', 'regionwb']]  # Store non-numerical data for later
                df = df.drop(columns=['economycode', 'economy', 'regionwb']) 
                print(f"🧪 Target col: {TARGET_COL}")
                print(f"📉 Before dropna: df shape = {df.shape}")
                print(f"📊 All columns: {df.columns.tolist()}")
                feature_cols = [col for col in df.columns if col != TARGET_COL]
                print("🧐 Null counts per column BEFORE dropna:\n", df[feature_cols].isnull().sum().sort_values(ascending=False))
                print(f"🧪 Unique values BEFORE filtering:\n{df[TARGET_COL].value_counts(dropna=False)}")
                df = df.dropna()
               
                print(f"📉 After dropna: df shape = {df.shape}")
                print(f"🧪 Unique values AFTER dropna:\n{df[TARGET_COL].value_counts(dropna=False)}")

                if "year" in df.columns:
                    df = df[df["year"] == YEAR_FILTER]
                else:
                    print("⚠️ Warning: 'year' column not found in DataFrame. Skipping filter.")

                df["pop_adult_scaled"] = np.log1p(df["pop_adult"])  # Log scaling
                df.drop(columns=["pop_adult"], inplace=True) 

                df = do_ul_cluster(df)
                # Replace column names with the modified ones from the processed dictionary
                # df.rename(columns=MODIFIED_DATA_DICT, inplace=True)
                df.to_pickle(PROCESSED_TRAIN_PATH)
                print(f"DataFrame updated and saved as pkl file: {PROCESSED_TRAIN_PATH}")

                if not os.path.exists(ECONOMY_SAVE_PATH):
                    economy_column.to_pickle(ECONOMY_SAVE_PATH)
                    print(f"Economy coding separated and saved as pkl file: {ECONOMY_SAVE_PATH}")

            except FileNotFoundError:
                print(f"Error: The file '{TRAIN_PATH}' was not found.")
                return None
            except Exception as e:
                print(f"Error loading data: {e}")
                return None
        else:
            #load pickl
            df = pd.read_pickle(PROCESSED_TRAIN_PATH)
        # target_col = MODIFIED_DATA_DICT[TARGET_COL]
        Y_df = df[TARGET_COL]  # Target variable
        X_df = df.drop(columns=[ TARGET_COL])
        print(f"✅ Final target value distribution:\n{Y_df.value_counts(dropna=False)}")

    else: 
        print("#"*18)
        raise ValueError("Invalid dataset specified. Check config.py")
    
    if not isinstance(X_df, pd.DataFrame):
        X_df = pd.DataFrame(X_df)  # Convert to DataFrame
    if Y_df.ndim == 1:
        # If it's 1D, convert to Pandas Series
        Y_df = pd.Series(Y_df)
    else:
        # If it's 2D, convert to Pandas DataFrame
        Y_df = pd.DataFrame(Y_df)

    print(f"   🔸 Y_df shape: {Y_df.shape}, unique: {Y_df.unique()}")
    print(f"   🔸 First 5 y: {Y_df.head().tolist()}")
    return X_df, Y_df

def graph_raw_data(X_df, Y_df):
    raw_data_outpath =OUTPUT_DIR_RAW_DATA_A3
    
    # Check if Y_df is multi-label (2D) or single-label (1D)
    if Y_df.ndim == 1:  # Single-label
        if not os.path.exists(f'{raw_data_outpath}/feature_heatmap_1.png'):
            if X_df.shape[0] > 1000:
                random_subset = X_df.sample(n=1000, random_state=42).index
                X_df = X_df.loc[random_subset]
                Y_df = Y_df.loc[random_subset]
            
            chunk_size = 12
            feature_list = list(X_df.columns) 
            feature_groups = [feature_list[i:i + chunk_size] for i in range(0, len(feature_list), chunk_size)]
            for i, feature_subset in enumerate(feature_groups):
                X_subset = X_df[feature_subset]  # Subset of features

                plots.graph_feature_violin(X_subset, Y_df, 
                                        f'{raw_data_outpath}/feature_violin_{i+1}.png')
                plots.graph_feature_heatmap(X_subset, Y_df,
                                            f'{raw_data_outpath}/feature_heatmap_{i+1}.png')
                plots.graph_feature_histogram(X_subset, 
                                            f'{raw_data_outpath}/feature_histogram_{i+1}.png')
                plots.graph_feature_correlation(X_subset, Y_df,
                                                f'{raw_data_outpath}/feature_correlation_{i+1}.png')
                plots.graph_feature_cdf(X_subset, 
                                        f'{raw_data_outpath}/feature_cdf_{i+1}.png')

            print(f"Generated {len(feature_groups)} sets of plots, each with up to {chunk_size} features.")

    else:  # Multi-label
        if not os.path.exists(f'{raw_data_outpath}/feature_heatmap.png'):
            # Handle multi-label plotting differently if necessary
            pass




def get_test_data():
    print(f"Getting test data for {DATASET_SELECTION}")
    if "kaggle_findex" in DATASET_SELECTION:
        solution_id_outpath = os.path.join(os.getcwd(), 'data', 'solution_id.csv')

        if not os.path.exists(PROCESSED_TEST_PATH):
            try:
                df = pd.read_csv(TEST_PATH)
                print("Accessed .csv in data folder")
                df = convert_and_normalize_days_since_policy_start(df, 'Policy Start Date')


                with open(f"{LABEL_ENCODERS_PKL_OUTDIR}/lencoders.pkl", "rb") as f:
                    encoders = pickle.load(f)
                print("got here")
                df, encoders =  handle_null_and_transform(df,encoders)

                columns_to_drop = ['id', 'Age']
                solution_id = df['id'].copy()
                with open(solution_id_outpath, "wb") as f:
                    pickle.dump(solution_id, f)
                print(f"Solution IDs saved at {solution_id_outpath}")

                df.drop(columns=columns_to_drop, inplace=True)
                nan_summary = df.isnull().sum()
                print("Missing values in each column:")
                print(nan_summary[nan_summary > 0])
                df.to_pickle(PROCESSED_TEST_PATH)
                print(f"DataFrame updated and saved as pickle file: {PROCESSED_TEST_PATH}")
                X_df = df
            except FileNotFoundError:
                print(f"Error: The file '{TEST_PATH}' was not found.")
                return None
            except Exception as e:
                print(f"Error loading data: {e}")
                return None
        else:
            X_df = pd.read_pickle(PROCESSED_TEST_PATH)
            solution_id_df = pd.read_pickle(solution_id_outpath)
            
            solution_id = pd.DataFrame(solution_id_df.values, columns=['id'])
            print(solution_id.head())
        print(X_df.info())
        print(solution_id.info())
    else: 
        print("#"*18)
        raise ValueError("Invalid dataset specified. Check config.py")
    if not isinstance(X_df, pd.DataFrame):
        X_df = pd.DataFrame(X_df)  # Convert to DataFrame

   
    return X_df, solution_id

import pandas as pd




def prelim_view(file_path, show_only_no_null=False):
    try:
        # Load the CSV file
        df = pd.read_csv(file_path, encoding="ISO-8859-1")  # or encoding="latin1" "utf-8"

        # Print general dataset info
        print("Dataset Overview:")
        print("#" * 50)
        print(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")
        print("#" * 50)

        print("Accessed .csv in data folder")
      

        # Prepare and print table-like summary for each column
        if not show_only_no_null:
            print(f"Total Missing Values: {df.isnull().sum().sum()}")
            print(f"{'Column':<20} {'Type':<10} {'# Unique':<10} {'Description':<50} {'Top 3 Values (Freq)':<50} {'# Null':<10} {'# Null %':<10} ")
            print("=" * 120)
            for col in df.columns:
                try:
                    col_type = str(df[col].dtype)  # Convert dtype to string to avoid formatting issues
                    col_desc = str(FINDEX_DATA_DICT[col])
                    unique_count = df[col].nunique() if "float" not in col_type and "int" not in col_type else "Numerical"
                    top_values = df[col].value_counts().head(3)
                    top_values_str = ", ".join([f"{val} ({cnt})" for val, cnt in top_values.items()])
                    null_count = df[col].isnull().sum()
                    null_perc = 100 * df[col].isnull().sum() / df[col].shape[0]
                    print(f"{col:<20} {col_type:<10} {unique_count:<10} {col_desc:<50}  {top_values_str:<50} {null_count:<10} {null_perc:.2f}%")
                except:
                    print(f"Column {col} not in FINDEX_DATA_DICT of 2021")

                
        else:
            print(f"{'Column':<20} {'Type':<10} {'# Unique':<10} {'Description':<50} {'Top 3 Values (Val: PercFreq)':<50}")
            print("=" * 120)
            for col in df.columns:
                if df[col].isnull().sum() > 0:
                    continue
                else:
                    try:
                        col_type = str(df[col].dtype)  # Convert dtype to string to avoid formatting issues
                        col_desc = str(FINDEX_DATA_DICT[col])
                        unique_count = df[col].nunique() #if "float" not in col_type and "int" not in col_type else "Numerical"
                        top_values = df[col].value_counts().head(3)
                        top_values_str = ", ".join([f"{val}: {100*cnt/df.shape[0]:.1f}%" for val, cnt in top_values.items()])
                        print(f"{col:<20} {col_type:<10} {unique_count:<10} {col_desc:<50} {top_values_str:<50} ")
                    except:
                        print(f"Column {col} not in FINDEX_DATA_DICT of 2021")
                   
                   
                    
            # for col in df.columns:
            #     if df[col].isnull().sum() == 0:
            #         print(col)

        print("=" * 120)
        # print("Note: Columns with numerical data are marked as 'Numerical' in the '# Unique' field.")
    except Exception as e:
        print(f"An error occurred while processing the file: {e}")



def drop_null_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows with any null values."""
    return df.dropna()

def drop_null_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Drop columns with any null values."""
    return df.dropna(axis=1)

def fill_null_with_value(df: pd.DataFrame, column: str, value) -> pd.DataFrame:
    """Fill null values in a specific column with a given value."""
    df[column].fillna(value, inplace=True)
    return df

def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicate rows."""
    return df.drop_duplicates()

def normalize_column(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Apply min-max normalization to a column."""
    df[column] = (df[column] - df[column].min()) / (df[column].max() - df[column].min())
    return df

def log_transform(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Apply log transformation to a column."""
    df[column] = df[column].apply(lambda x: x if x <= 0 else pd.np.log(x))
    return df


def custom_etl_v1(df: pd.DataFrame) -> pd.DataFrame:
    try:
        available_columns = [col for col in COLUMNS_TO_KEEP + [TARGET_COL] if col in df.columns]
        df = df[available_columns]
        economy_column = df['economy' ]  # Store non-numerical data for later

        df = df.drop(columns=['economycode', 'economy']) 
        df = drop_null_rows(df)

        if "year" in df.columns:
            df = df[df["year"] == YEAR_FILTER]
        else:
            print("⚠️ Warning: 'year' column not found in DataFrame. Skipping filter.")

        df["pop_adult_scaled"] = np.log1p(df["pop_adult"])  # Log scaling
        df.drop(columns=["pop_adult"], inplace=True) 

        df = do_ul_cluster(df)
        # df.rename(columns=MODIFIED_DATA_DICT, inplace=True)
        return df
    
    except Exception as e:
        print(f"Error loading data: {e}")
        return None


# Dictionary mapping function names to actual functions
ETL_FUNCTIONS = {
    "drop_null_rows": drop_null_rows,
    "drop_null_columns": drop_null_columns,
    "fill_null_with_value": fill_null_with_value,
    "remove_duplicates": remove_duplicates,
    "normalize_column": normalize_column,
    "log_transform": log_transform,
    "custom_etl_v1": custom_etl_v1,
}
