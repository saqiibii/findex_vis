from config import *
# from src.models import *
from utils import *
from tests import *

import etl as etl
import plots as plots
import hypotheses as hypotheses

import pickle
import glob
import re
import time
import os
# from datetime import datetime
import datetime

import unittest
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate 
import pickle
import random
from copy import deepcopy
import math
import itertools
import joblib
import xgboost as xgb
from xgboost import XGBClassifier
from sklearn.svm import SVC

from scipy.stats import gaussian_kde
from scipy.stats import ttest_1samp
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import confusion_matrix,precision_score, \
                        recall_score,classification_report, \
                        accuracy_score, f1_score, log_loss, \
                       confusion_matrix, ConfusionMatrixDisplay,\
                          roc_auc_score, matthews_corrcoef, average_precision_score, \
                          mean_squared_error, mean_absolute_error, r2_score
from sklearn.cluster import KMeans, AgglomerativeClustering,DBSCAN,Birch,MeanShift, SpectralClustering
from sklearn.mixture import GaussianMixture
from sklearn.model_selection import ParameterSampler, KFold
#import dimension reduction modules
from sklearn.decomposition import PCA, FastICA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.random_projection import GaussianRandomProjection, SparseRandomProjection



from torch import nn, optim
import torch
from torch.utils.data import DataLoader, TensorDataset

import pickle
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor, HistGradientBoostingRegressor, BaggingRegressor, GradientBoostingRegressor
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier, ExtraTreesClassifier, HistGradientBoostingClassifier, BaggingClassifier
from sklearn.model_selection import GridSearchCV, train_test_split


def train_nn_with_early_stopping_with_param(X_train, y_train, X_test, y_test, params, max_epochs, patience, model_name="default"):
    lr = params['lr']
    batch_size = params['batch_size']
    hidden_layers = params['hidden_layers']
    dropout_rate = params['dropout_rate']
    input_dim = X_train.shape[1]
    if len(y_train.shape) > 1 and y_train.shape[1] > 1:
        # Multi-label classification (y_train has multiple labels per instance)
        output_dim = y_train.shape[1]  # Number of labels
    else:
        # Single-label classification (y_train has a single label per instance)
        output_dim = len(np.unique(y_train.cpu())) 
    if model_name == "default":
        model = SimpleNN(input_dim, output_dim, hidden_layers, dropout_rate=dropout_rate).to(device)
    elif model_name == "MPL":
        model = NNMPL(input_dim=input_dim, output_dim=output_dim).to(device)
    elif model_name == "CNN":
        model = NNCNN(input_dim=input_dim, output_dim=output_dim,hidden_dim=289, feature_maps=19, dropout_rate=params['dropout_rate']).to(device)

    elif model_name == "LSTM":
        model = NNLSTM(input_dim=input_dim, output_dim=output_dim,hidden_dim=289, lstm_hidden_dim=300, dropout_rate=params['dropout_rate']).to(device)

    elif model_name == "bi-LSTM":
        model = NNBiLSTM(input_dim=input_dim, output_dim=output_dim,  hidden_dim=289, lstm_hidden_dim=150, dropout_rate=params['dropout_rate']).to(device)

    elif model_name == "conv-LSTM":
        model = NNConvLSTM(input_dim=input_dim, output_dim=output_dim,  hidden_dim=289, feature_maps=19, lstm_hidden_dim=300, dropout_rate=params['dropout_rate']).to(device)

    else:
        raise ValueError(f"Unsupported model type: {model_name}")
    # model = NNMPL(input_dim, output_dim, dropout_rate).to(device)



    if len(y_train.shape) == 1:  
        criterion = nn.CrossEntropyLoss()  # For single label classification (multi-class)
    else:  
        criterion = nn.BCEWithLogitsLoss()  # For multi-label classification

    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    train_dataset = TensorDataset(X_train, y_train)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    best_val_loss = float('inf')
    epochs_without_improvement = 0
    epoch_trained = 0

    epoch_losses = []
    start_time = time.time()
    print("Starting training loop...")
    for epoch in range(max_epochs):
        epoch_start_time = time.time()
        epoch_trained+=1
        model.train()

        running_loss = 0.0
        for batch_x, batch_y in train_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            optimizer.zero_grad()
            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()

        avg_epoch_loss = running_loss / len(train_loader)
        # Validation
        val_loss = evaluate_model(model, X_test, y_test, device,criterion)
        epoch_losses.append((avg_epoch_loss,val_loss))
        print(f"Epoch {epoch}, last train_loss {epoch_losses[-1][0]:.5F} val_loss {val_loss:.5F} per {criterion}")
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1
        if epochs_without_improvement >= patience:
            break
        epoch_runtime = time.time() - epoch_start_time
        print(f"Epoch completed in {epoch_runtime // 60:.0f}m {epoch_runtime % 60:.0f}s\n")
    runtime = time.time() - start_time
    print(model)
    print(f"Model {model_name} Training completed in {runtime // 60:.0f}m {runtime % 60:.0f}s\n")
    print(f"Average time per epoch: {(runtime / epoch_trained )//60:.0f}m {(runtime / epoch_trained)%60:.0f}s")

    # Evaluate the model
    model.eval()
    with torch.no_grad():
        outputs = model(X_test)

        _, predicted = torch.max(outputs, 1)

        if y_train.shape[1] > 1:
            test_outputs_np = outputs.sigmoid().cpu().numpy()  # Sigmoid for multi-label probability
           
            y_test = y_test.cpu().numpy()
            best_threshold = .5
            predicted = (test_outputs_np >= best_threshold).astype(int)
            # Calculate accuracy, AUC-ROC, and F1-score for multi-label classification
            # Individual label accuracy (mean accuracy for each label)
            label_accuracy = (predicted == y_test).mean(axis=0)
            accuracy = label_accuracy.mean()  # Average accuracy across all labels
            try:
                auc_roc = roc_auc_score(y_test, test_outputs_np, average="macro")
            except ValueError:
                auc_roc = float("nan")  # Handle cases where AUC-ROC can't be calculated
            f1 = f1_score(y_test, predicted, average="macro")
            mcc = matthews_corrcoef(y_test.flatten(), predicted.flatten())
            auprc = average_precision_score(y_test, test_outputs_np, average="macro")

        #if y is single label
        else:
            accuracy = accuracy_score(y_test.cpu(), predicted.cpu())
            f1 = f1_score(y_test.cpu(), predicted.cpu(), average='weighted')
            # probs = torch.softmax(outputs, dim=1)
            # auc_roc = roc_auc_score(y_test.cpu(), probs.cpu(), multi_class='ovr')  # For multi-class problems
            probs = torch.sigmoid(outputs)[:, 0]  # Assuming the positive class is the first one
            auc_roc = roc_auc_score(y_test.cpu(), probs.cpu())
            mcc = matthews_corrcoef(y_test.cpu(), predicted.cpu())
            auprc = average_precision_score(y_test.cpu(), probs.cpu())


        ##################
    print(f"Training terminated after epoch {epoch_trained}, "
            f"Avg Label Accuracy: {accuracy:.4f}, "
            f"AUC-ROC: {auc_roc:.4f}, "
            f"F1-Score: {f1:.4f}, "
            f"MCC: {mcc:.4f}, "
            f"AU-PRC: {auprc:.4f}")


    
    return accuracy, f1,auc_roc, mcc, auprc, runtime,model,epoch_losses,y_test,predicted


def get_eval_reg_with_nn(X,y,nn_performance_path,cv_losses_outpath, y_pred_outpath, do_cv = 1):
    if not os.path.exists(nn_performance_path) or not os.path.exists(cv_losses_outpath) or not os.path.exists(y_pred_outpath):
        X = pd.DataFrame(X)  # Assuming X_train is a DataFrame
        X = torch.FloatTensor(X.values).to(device)
        y = torch.FloatTensor(y).to(device)
        nn_results={}

        ###################################
        for model_name in EVAL_REG_MODELS:
            # avg_metric_per_cv = [0 for _ in range(K_FOLD_CV)] if do_cv else [0]
            # Initialize placeholders for cross-validation metrics
            avg_metrics_per_cv = {
                "mse": [],
                "mae": [],
                "rmse": [],
                "r2": [],
                "runtime": []
            }
            cv_losses = []
            y_preds = []
            
            for fold_idx, (train_idx, val_idx) in enumerate(kf.split(X) if do_cv else [(range(len(X)), range(len(X)))]):
                print(f"Starting fold {fold_idx + 1}")
                X_train, X_val = X[train_idx], X[val_idx]
                y_train, y_val = y[train_idx], y[val_idx]

                best_cv_perfs, best_params,best_eval_func, best_models_ensemble = reg_hyperparameter_tuning(X_train, y_train, X_val, y_val, device, model_name)


def get_eval_with_nn(X,y,nn_performance_path,cv_losses_outpath, y_pred_outpath, do_cv = 1):
    if not os.path.exists(nn_performance_path) or not os.path.exists(cv_losses_outpath):
        X = pd.DataFrame(X)  # Assuming X_train is a DataFrame
        X = torch.FloatTensor(X.values).to(device)
        y = torch.FloatTensor(y).to(device)
        nn_results={}

        param_combinations = list(itertools.product(*PARAM_GRID.values()))

        ###################################
        for model_name in EVAL_MODELS:
            for params in param_combinations:
                current_params = {
                    'lr': params[0],
                    'batch_size': params[1],
                    'dropout_rate': params[2],
                    'hidden_layers': params[3],
                }

                current_metrics_of_Xy = []

                avg_metric_per_cv = [0 for _ in range(K_FOLD_CV)] if do_cv else [0]
                cv_losses = []
                y_preds = []
                
                for fold_idx, (train_idx, val_idx) in enumerate(kf.split(X) if do_cv else [(range(len(X)), range(len(X)))]):
                    print(f"Starting fold {fold_idx + 1}")
                    X_train, X_val = X[train_idx], X[val_idx]
                    y_train, y_val = y[train_idx], y[val_idx]
                    
                    # Train and evaluate model with current parameters
                    accuracy, f1,auc_roc,mcc, auprc, runtime,temp_model,epoch_losses,y_test,predicted = train_nn_with_early_stopping_with_param(
                        X_train, y_train, X_val, y_val, current_params,NN_MAX_EPOCH, NN_PATIENCE, model_name,
                    )
                    
                    # Store the current metrics
                    current_metrics_of_Xy.append((accuracy, f1, runtime, auc_roc,mcc, auprc))
                    
                    # Choose evaluation metric
                    if "f1" in EVAL_FUNC_METRIC:
                        avg_metric_per_cv[fold_idx] = f1
                    elif "accuracy" in EVAL_FUNC_METRIC:
                        avg_metric_per_cv[fold_idx] = accuracy
                    elif "auc" in EVAL_FUNC_METRIC:
                        avg_metric_per_cv[fold_idx] = auc_roc
                    cv_losses.append(epoch_losses)
                    y_preds.append((y_test,predicted))

            # Calculate average metric across folds
            avg_metric = np.mean(avg_metric_per_cv)
            
            # Update running best if the new metric is better
            if avg_metric > inner_cv_running_best_metric:
                inner_cv_running_best_metric = avg_metric

            if inner_cv_running_best_metric > outer_ro_running_best_metric:
                outer_ro_running_best_metric = inner_cv_running_best_metric
                running_best_y_preds = y_preds
                avg_accuracy, std_accuracy, avg_mcc, avg_f1, avg_roc_auc, avg_pr_auc = get_metrics_of_hyperparm_set(y_preds)
            
                running_best_result_dict = {
                    'model_name': model_name,
                    'avg_accuracy': avg_accuracy,
                    'std_accuracy': std_accuracy,  # Save the standard deviation for accuracy
                    'avg_mcc': avg_mcc,
                    'avg_f1': avg_f1,
                    'avg_roc_auc': avg_roc_auc,
                    'avg_pr_auc': avg_pr_auc,
                    'max_epoch': NN_MAX_EPOCH,
                    'current_params': current_params,
                    'current_metrics_of_Xy': current_metrics_of_Xy,
                    'y_preds': y_preds,
                    'cv_losses': cv_losses,
                    
                }
            
                with open(stats_filename, 'w') as f:
                    f.write(f"Model: {model_name}\n")
                    f.write(f"Average Accuracy: {avg_accuracy:.4f} ± {std_accuracy:.4f}\n")
                    f.write(f"Average MCC: {avg_mcc:.4f}\n")
                    f.write(f"Average F1 Score: {avg_f1:.4f}\n")
                    f.write(f"Average AUC-ROC: {avg_roc_auc:.4f}\n")
                    f.write(f"Average AUC-PR: {avg_pr_auc:.4f}\n")
                    f.write(f"max_epoch: {NN_MAX_EPOCH}\n")
                    f.write(f"Hyperparameters: {current_params}\n")
                print(f"Saved stats to {stats_filename}")

            best_overall_metric, best_overall_model, best_overall_method, running_metrics_Xy_srx_space, \
                best_overall_cv_losses,running_best_y_preds,running_best_result_dict = run_model_tuning_RO_for_Xy_srx_space(
                    X_features, 
                    y_labels, 
                    do_cv=True, 
                    random_opt_algo="default", 
                    best_overall_metric=best_overall_metric,  # Keyword argument
                    best_overall_method=best_overall_method,    # Keyword argument
                    best_overall_model=best_overall_model,    # Keyword argument
                    best_overall_cv_losses = best_overall_cv_losses,
                    type_tag=f"NN_{model_name}",             # Keyword argument,
                    model_name = model_name,
                )
            nn_results[model_name] = {'mc_results': running_metrics_Xy_srx_space}
            with open(f'{NN_PKL_OUTDIR}/NN_best_{model_name}_hyperparam_set.pkl', 'wb') as f:
                pickle.dump(running_best_result_dict,f)
            with open(f'{Y_PRED_PKL_OUTDIR}/y_pred_best_of_{model_name}.pkl', 'wb') as f:
                pickle.dump(running_best_y_preds,f)
            print(f"Saved results to {Y_PRED_PKL_OUTDIR}/y_pred_best_of_{model_name}.pkl")
        with open(f'{NN_PKL_OUTDIR}/NN_best_of_{model_name}_nn_results.pkl', 'wb') as f:
            pickle.dump(nn_results,f)
        print(f"Saved results to {NN_PKL_OUTDIR}/NN_best_of_{model_name}_nn_results.pkl")

def evaluate_metrics_in_context(y_true, y_pred, model_name, file_path=f"{TXT_OUTDIR}/dt_model_results.txt"):
    print("Statistics for y_test (Actual values):")
    print(f"Count: {len(y_true)}")
    print(f"Mean: {np.mean(y_true):.2f}")
    print(f"Standard Deviation: {np.std(y_true):.2f}")
    print(f"Min: {np.min(y_true)}")
    print(f"Max: {np.max(y_true)}")
    print(f"Unique values: {len(np.unique(y_true))}")

    print("\nStatistics for y_pred (Predicted values):")
    print(f"Count: {len(y_pred)}")
    print(f"Mean: {np.mean(y_pred):.2f}")
    print(f"Standard Deviation: {np.std(y_pred):.2f}")
    print(f"Min: {np.min(y_pred)}")
    print(f"Max: {np.max(y_pred)}")
    print(f"Unique values: {len(np.unique(y_pred))}")
    # Calculate MSE, MAE, and R²
    print(f"For model {model_name}:")
    mse = mean_squared_error(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    if np.any(np.isnan(y_true)):
        print("Warning: NaN values found in y_true")
    if np.any(np.isnan(y_pred)):
        print("Warning: NaN values found in y_pred")
    if np.any(y_true < 0) or np.any(y_pred < 0):
        raise ValueError("RMSLE cannot be calculated for negative values in y_true or y_pred.")
    if np.isnan(y_true).any() or np.isnan(y_pred).any():
        raise ValueError("RMSLE cannot be calculated because y_true or y_pred contains NaN values.")
    
    rmlse = np.sqrt(mean_squared_error(np.log1p(y_true), np.log1p(y_pred)))
    
    # Calculate average price for relative error calculations
    avg_price = np.mean(y_true)
    
    # Calculate relative MSE and MAE
    relative_mse = (mse / avg_price) * 100
    relative_mae = (mae / avg_price) * 100
    
    # Print results in context
    print(f"Mean Squared Error (MSE): {mse}")
    print(f"RMLSE: {rmlse}")
    print(f"Mean Absolute Error (MAE): {mae}")
    print(f"R² Score: {r2}")
    print(f"Relative MSE (% of avg price): {relative_mse:.2f}%")
    print(f"Relative MAE (% of avg price): {relative_mae:.2f}%")
    
    # Append the results to the file
    with open(file_path, "a") as log_file:
        log_file.write(f"\nFor model {model_name}:\n")
        log_file.write(f"Mean Squared Error (MSE): {mse}\n")
        log_file.write(f"RMLSE: {rmlse}\n")
        log_file.write(f"Mean Absolute Error (MAE): {mae}\n")
        log_file.write(f"R² Score: {r2}\n")
        log_file.write(f"Relative MSE (% of avg price): {relative_mse:.2f}%\n")
        log_file.write(f"Relative MAE (% of avg price): {relative_mae:.2f}%\n")
        log_file.write("\n" + "="*50 + "\n")
    
    # return mse, mae, r2, relative_mse, relative_mae

def train_and_evaluate_svm(X_train, y_train, X_test, y_test):
    kernels = ['linear', 'poly', 'rbf', 'sigmoid']
    results = {}

    # Train and evaluate for each kernel
    for kernel in kernels:
        print(f"\nTraining SVM with kernel: {kernel}")
        svm_model = SVC(kernel=kernel, C=1, gamma='scale', random_state=GT_ID)
        bins = [0, 100, 400, 900, 1600, 2500, 3000, 4000, 5000, np.inf]
        bin_labels = range(len(bins) - 1)
        binned_y_train = pd.cut(y_train, bins=bins, labels=bin_labels)
        bin_distributions = {}
        for bin_label in bin_labels:
            bin_values = y_train[binned_y_train == bin_label]
            value_counts = bin_values.value_counts(normalize=True)  # Relative frequencies
            bin_distributions[bin_label] = value_counts
        svm_model.fit(X_train, binned_y_train)
        binned_y_pred = svm_model.predict(X_test)
        y_pred = []
        for pred in binned_y_pred:
            bin_dist = bin_distributions[pred]
            sampled_value = np.random.choice(bin_dist.index, p=bin_dist.values)
            y_pred.append(sampled_value)
        y_pred = np.array(y_pred)

        binned_y_test = pd.cut(y_test, bins=bins, labels=bin_labels)
        accuracy = accuracy_score(binned_y_test, binned_y_pred)
        class_report = classification_report(binned_y_test, binned_y_pred)
        print(f"Kernel: {kernel}")
        print(f"Accuracy: {accuracy * 100:.2f}%")
        print("Classification Report:")
        print(class_report)

        # Store results
        results[kernel] = {
            'accuracy': accuracy,
            'classification_report': class_report
        }

    # Print summary of results
    print("\nSummary of Results:")
    for kernel, metrics in results.items():
        print(f"Kernel: {kernel}")
        print(f"Accuracy: {metrics['accuracy']}\n")

# Function to train and evaluate the Decision Tree Regressor with different configurations
def train_and_evaluate_dt(X_train, y_train, X_test, y_test, model_type = "Default Decision Tree", pred_type = "classifier"):

    # Initialize models
    if pred_type == "classifier":
        dt = DecisionTreeClassifier(random_state=GT_ID)
        boosting = GradientBoostingClassifier(n_estimators=N_ESTIMATOR, learning_rate=0.001, random_state=GT_ID)
        rf = RandomForestClassifier(n_estimators=N_ESTIMATOR, random_state=GT_ID)
        extra_trees = ExtraTreesClassifier(n_estimators=N_ESTIMATOR, random_state=GT_ID)
        hist_gb = HistGradientBoostingClassifier(max_iter=N_ESTIMATOR, random_state=GT_ID)
        svm_model = SVC(kernel='rbf', C=1, gamma='scale', random_state=42)  # No change needed, it's already a classifier
        bagging = BaggingClassifier(estimator=rf, n_estimators=N_ESTIMATOR, random_state=GT_ID)
    else:
        dt = DecisionTreeRegressor(random_state=GT_ID)
        boosting = GradientBoostingRegressor(n_estimators=N_ESTIMATOR, learning_rate=0.001, random_state=GT_ID)
        rf = RandomForestRegressor(n_estimators=N_ESTIMATOR, random_state=GT_ID)
        extra_trees = ExtraTreesRegressor(n_estimators=N_ESTIMATOR, random_state=GT_ID)
        hist_gb = HistGradientBoostingRegressor(max_iter=N_ESTIMATOR, random_state=GT_ID)
        svm_model = SVC(kernel='rbf', C=1, gamma='scale', random_state=42)
        bagging = BaggingRegressor(estimator = rf, n_estimators=N_ESTIMATOR, random_state=GT_ID)

    
    param_grid = {  'max_depth': [3, 5, 10],
                    'min_samples_split': [2, 5],
                    'min_samples_leaf': [1, 2]}
    grid_search = GridSearchCV(dt, param_grid, cv=5, scoring='neg_mean_squared_error')
    
    # Fit models
    models = {
        "Default Decision Tree": dt,
        "Bagging": bagging,
        # "Boosting with Decision Tree": boosting,
       
        "Random Forest": rf,
        # "Histogram-based Gradient Boosting": hist_gb,
        # "Tuned Decision Tree (GridSearch)": grid_search,
    }
    if isinstance(model_type, str):
        selected_models = [model_type]
    elif isinstance(model_type, list):
        selected_models = model_type
    else:
        raise ValueError("model_type must be a string or list of strings")
    models = {name: model for name, model in models.items() if name in selected_models}
    if not models:
        raise ValueError(f"No valid models selected. Available models: {list(models.keys())}")
    
    results = {}
    # print("getting smote")
    # smote = SMOTE(sampling_strategy='auto', random_state=42)
    # X_train, y_train = smote.fit_resample(X_train, y_train)
    for model_name, model in models.items():
        print("#"*18)
        print(model,model_name)
        start_time = time.time()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        if np.any(np.isnan(y_test)):
            print("Warning: NaN values found in y_test")
        if np.any(np.isnan(y_pred)):
            print("Warning: NaN values found in y_pred")

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        model_path = os.path.join(
            MODELS_OUTDIR,
            f"{model_name}_{timestamp}.joblib"
        )

        if PRED_TYPE == "classifier":
            metric_average = 'binary' if len(np.unique(y_test)) == 2 else 'weighted'
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average=metric_average)  
            recall = recall_score(y_test, y_pred, average=metric_average)  
            f1 = f1_score(y_test, y_pred, average=metric_average)  
            roc_auc = roc_auc_score(y_test, y_pred) if len(np.unique(y_test)) == 2 else 0  
            model_params = model.get_params() if hasattr(model, 'get_params') else 0
            results[model_name] = {
                "Accuracy": accuracy,
                "Precision": precision,
                "Recall": recall,
                "F1_score": f1,
                "ROC_AUC": roc_auc,
                "runtime": time.time() - start_time,
                'params': model_params,
                "y_pred": y_pred,
                "model": model,

            }
            log_entry = (
                f"Model: {model_name}\n"  # Ensure this is properly indented
                f"Saved Path: {model_path}\n"
                f"Timestamp: {timestamp}\n"
                f"Accuracy: {results[model_name]['Accuracy']:.4f}\n"
                f"Precision: {results[model_name]['Precision']:.4f}\n"
                f"Recall: {results[model_name]['Recall']:.4f}\n"
                f"F1 Score: {results[model_name]['F1_score']:.4f}\n"
                f"ROC AUC: {results[model_name]['ROC_AUC']:.4f}\n"
                f"Runtime: {results[model_name]['runtime']:.2f} seconds\n"
                f"Model Hyperparameters: {model_params}\n"
                f"{'#' * 50}\n"
            )
        else:
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            rmlse = np.sqrt(mean_squared_error(np.log1p(y_test), np.log1p(y_pred)))
            model_params = model.get_params() if hasattr(model, 'get_params') else None

            results[model_name] = {
                "MSE": mse,
                "MAE": mae,
                "RMSE": rmse,
                "RMLSE": rmlse,
                "R2": r2,
                "runtime": time.time() - start_time,
                'params': model_params,
                "y_pred": y_pred,
            }
            log_entry = (
                f"Model: {model_name}\n"
                f"Saved Path: {model_path}\n"
                f"Timestamp: {timestamp}\n"
                f"MSE: {results[model_name]['MSE']:.4f}\n"
                f"MAE: {results[model_name]['MAE']:.4f}\n"
                f"RMSE: {results[model_name]['RMSE']:.4f}\n"
                f"RMLSE: {results[model_name]['RMLSE']:.4f}\n"
                f"R2: {results[model_name]['R2']:.4f}\n"
                f"Runtime: {results[model_name]['runtime']:.2f} seconds\n"
                f"Model Hyperparameters: {model_params}\n"  
                f"{'#' * 50}\n"
            )
        
        # Append the log entry to the text file
        with open(MODEL_ALL_LOG_FILE, "a") as log_file:
            log_file.write(log_entry)
        ###############
        # evaluate_metrics_in_context(y_test, y_pred, model_name)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        plots.plot_predictions( y_test, y_pred,1, model_name,
                f"{AGGREGATED_OUTDIR}/{timestamp}_pred_actual_diff_{model_name}.png",
                # f"{AGGREGATED_OUTDIR}/{timestamp}_pred_actual_hist_{model_name}.png"
                )
    return results

# Function to train and evaluate the Decision Tree Regressor with different configurations
def train_and_evaluate_mpl_classification(X,y):
    # Initialize models
    results = {}
    X = torch.FloatTensor(X.values)
    y = torch.FloatTensor(y.values)
    for model_name in EVAL_REG_MODELS:
        model_start_time = time.time()
        best_cv_perfs, best_params,best_eval_func, best_models_ensemble = label_hyperparameter_tuning(X,y, device, model_name,1)
        results[model_name] = {
            "Accuracy": best_cv_perfs['Accuracy'],
            "Precision": best_cv_perfs['Precision'],
            "Recall": best_cv_perfs['Recall'],
            "F1": best_cv_perfs['F1'],
            "ROC AUC": best_cv_perfs['ROC AUC'],
            "All folds runtime": time.time() - model_start_time,
            "Per fold runtime": best_cv_perfs['runtime'],
            "params": best_params,
    }

    return results
        

def save_results(results,filename ):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'wb') as f:
        pickle.dump(results, f)
    print(f"Results saved to {filename}")

    if isinstance(results, pd.DataFrame):
        df = results  # Use directly if already a DataFrame
    elif isinstance(results, dict):
        df = pd.DataFrame.from_dict(results, orient="index")  # Convert dict to DataFrame
    elif isinstance(results, list):
        df = pd.DataFrame(results)  # Convert list of dicts to DataFrame
    else:
        print(f"⚠️ Warning: Unsupported results format ({type(results)}). Skipping CSV saving.")
        return

    base_filename = filename.rsplit(".", 1)[0]

    csv_filename = base_filename + ".csv"

    try:
        df.to_csv(csv_filename, index=True)  
        print(f"Results also saved as CSV: {csv_filename}")
    except Exception as e:
        print(f"⚠️ Warning: Failed to save as CSV. Error: {e}")
    
    json_filename = base_filename + ".json"
    try:
        df.to_json(json_filename, orient="records", indent=4)
        print(f"Results also saved as JSON: {json_filename}")
    except Exception as e:
        print(f"⚠️ Warning: Failed to save as JSON. Error: {e}")

def economy_stratified_split(X, y, test_size=TEST_SIZE, random_state=GT_ID):
    X_copy = X.copy()
    if os.path.exists(ECONOMY_SAVE_PATH):
        train_indices = []
        test_indices = []
        saved_columns = pd.read_pickle(ECONOMY_SAVE_PATH)
        print(X_copy.columns)
        print(saved_columns.columns)
        X_copy[['economy', 'pop_adult', 'regionwb']] = saved_columns[[
                                                    'economy', 'pop_adult', 'regionwb'
                                                ]]
        
        #also get #also return  y_test_population, y_test_region  from here
        print(f"Loaded economy coding from: {ECONOMY_SAVE_PATH}")
        for economy in X_copy["economy"].unique():
            econ_indices = X_copy[X_copy["economy"] == economy].index
            econ_train, econ_test = train_test_split(econ_indices, test_size=test_size, random_state=random_state)
            train_indices.extend(econ_train)
            test_indices.extend(econ_test)

        y_test_economy = X_copy.loc[test_indices, "economy"].copy()
        y_test_population = X_copy.loc[test_indices, "pop_adult"].copy()
        y_test_region = X_copy.loc[test_indices, "regionwb"].copy()
        X_copy = X_copy.drop(columns = ['economy','regionwb', 'pop_adult'])
        return X_copy.loc[train_indices], X_copy.loc[test_indices], \
            y.loc[train_indices], y.loc[test_indices], \
            y_test_economy, y_test_population, y_test_region
    else:
        print("Economy save path not found. Using random split.")
        return train_test_split(X, y, test_size=test_size, random_state=random_state) + (None,)

    
    

def check_etl():
    X, y = etl.get_data()
    # print(y)
    X_train, X_test, y_train, y_test, y_test_economy, y_test_population, y_test_region = economy_stratified_split(X, y)
   
    # test_data_etl_input_check(X,y,X_train, X_test, y_train, y_test, show = True)
    ####
    # etl.graph_raw_data(X, y)
    # plots.analyze_feature_importance(X_train, y_train, f"")
    # plots.analyze_dim_reduc(X_train,y_train,X_test, y_test)
    
    print("======> Data verification complete")
    return X,y,X_train, X_test, y_train, y_test, y_test_economy, y_test_population, y_test_region

def get_solutions(X_train):
    X_test, solution_id = etl.get_test_data()
    model_files = [f for f in os.listdir(MODELS_OUTDIR) if f.endswith('.joblib')]
    inferred_models = []
    for model_file in model_files:
        print(model_file)
        inferred = False
        model_name = ''
        # Check if models with folds aka MPL 
        if "_fold_" in model_file:
            model_name = model_file.split('_fold_')[0]
            result_file =  os.path.join(SOLUTIONS_OUTDIR, f"solutions_{model_name}.csv") 
            if not os.path.exists(result_file) and model_name not in inferred_models:
                fold_models = [
                    joblib.load(os.path.join(MODELS_OUTDIR, model_file))
                    for model_file in model_files if model_file.startswith(f"{model_name}_fold_")
                ]

                for model in fold_models:
                    model.eval()
                
                # Prepare data for PyTorch models
                X_test_tensor = torch.FloatTensor(X_test.values)  # Convert X_test to a tensor
                test_dataset = TensorDataset(X_test_tensor)  # Wrap it in a TensorDataset
                test_loader = DataLoader(test_dataset, batch_size=1024, shuffle=False)  # Use a suitable batch size
                
                # Make predictions with each model
                predictions_list = []

                # Make predictions with each model
                predictions_list = []
                with torch.no_grad():  # Disable gradient computation for evaluation
                    for model in fold_models:
                        batch_predictions = []
                        for batch in test_loader:
                            batch_X = batch[0].to(device)  # Move batch data to GPU
                            batch_pred = model(batch_X).cpu().numpy()  # Move predictions to CPU
                            batch_predictions.append(batch_pred)
                        predictions_list.append(np.concatenate(batch_predictions, axis=0))
                
                        # predictions = model(X_test_tensor).cpu().numpy()  # Move predictions to CPU
                        # predictions_list.append(predictions)
                
                # Average predictions from all fold models
                predictions = np.mean(predictions_list, axis=0)
                inferred_models.append(model_name)
                inferred = True
            else:
                print(f"Model {model_name} solutions already created at {result_file}")
        else: #no CV aka DT models
            model_name = model_file.split('_')[0]
            result_file =  os.path.join(SOLUTIONS_OUTDIR, f"solutions_{model_name}.csv") 
            if not os.path.exists(result_file) and model_name not in inferred_models:
                print(f"Loading individual model for {model_name}")
                model = joblib.load(os.path.join(MODELS_OUTDIR, model_file))
                predictions = model.predict(X_test)
                inferred_models.append(model_name)
                inferred = True
            else:
                print(f"Model {model_name} solutions already created at {result_file}")
        if inferred:
            print(f"solution_id shape: {solution_id.shape}")
            print(f"predictions shape: {predictions.shape}")
            predictions = predictions.squeeze() if predictions.ndim > 1 else predictions
            solution_id = solution_id.squeeze() if isinstance(solution_id, pd.DataFrame) else solution_id
            results_df = pd.DataFrame({
                'id': solution_id,
                'Premium Amount': predictions.squeeze(),
            })
            
            results_df.to_csv(result_file, index=False)
            print(f"Predictions for {model_name} saved in {result_file}")
###############
def main(): 
    np.random.seed(GT_ID)
  
    do_skl_train = 1
    do_torch_train = 0
    start_time = time.time()
    X,y,X_train, X_test, y_train, y_test, y_test_economy_codes, y_test_population, y_test_region  = check_etl()
    check_data_info(X, y, X_train, X_test, y_train, y_test, show = False)
    print(f"Time to load data: {time.time() - start_time}s")
    ###### Sklearn models (just DT for now)
    if do_skl_train:
        print("starting skl models")
        results_dt = train_and_evaluate_dt(X_train, y_train, X_test, y_test)

        save_results(results_dt, f"{Y_PRED_OUTDIR}/test{DRAFT_VER_A3}/dt_results.pkl")
        save_trained_models(results_dt, f"{Y_PRED_OUTDIR}/test{DRAFT_VER_A3}/models/")
        # print(y_test)
        test_results_df = X_test.copy()
        test_results_df["y_test"] = y_test.values  
        for model_name, model_results in results_dt.items():
            model_name_formatted = model_name.lower().replace(" ", "_")
            test_results_df[f"y_pred_{model_name_formatted}"] = model_results["y_pred"]  #ea. predictions
        #
        test_results_df["economy_code"] = y_test_economy_codes  
        
         


        # serialize to pickle
        save_results(test_results_df, f"{Y_PRED_OUTDIR}/{DRAFT_VER_A3}/raw_test_set_with_pred.pkl")

        trained_models = {name.lower().replace(" ", "_"): model_results["model"] for name, model_results in results_dt.items()}
        test_results_df["population"] = y_test_population
        test_results_df["regionwb"] = y_test_region
        metrics_df, feature_importance_df, metrics_list_by_cluster = ml_perf_eval_by_country(test_results_df, trained_models)
        
        
        save_results(metrics_df, f"{Y_PRED_OUTDIR}/test{DRAFT_VER_A3}/metrics_by_countries.pkl")
        save_results(feature_importance_df, f"{Y_PRED_OUTDIR}/test{DRAFT_VER_A3}/ft_importance.pkl")
        save_results(metrics_list_by_cluster, f"{Y_PRED_OUTDIR}/test{DRAFT_VER_A3}/metrics_by_cluster.pkl")
        
    ####### Torch models 
    if do_torch_train:
        print("starting torch models")
        mpl_result_save_file = f"{Y_PRED_OUTDIR}/mpl_results.pkl"
        # if not os.path.exists(mpl_result_save_file) or os.path.exists(mpl_result_save_file):
        results = train_and_evaluate_mpl_classification(X,y)
        save_results(results, f"{Y_PRED_OUTDIR}/mpl_results.pkl")
        
    ######## for kaggle - done training, now infer to solutions.csv
    # get_solutions(X_train)
    

if __name__ == "__main__":
    ###################
    print("PyTorch mps check: ",torch.backends.mps.is_available())
    print("PyTorch cuda check: ",torch.cuda.is_available())
    if torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Torch will be running on {device}")
    ####################
    # etl.prelim_view(TRAIN_PATH)
    
    main()
    

    #run model with fewer features for explainability

# mlAPI/ml.py

def run_prediction(model_type: str = "Default Decision Tree"):
    np.random.seed(GT_ID)

    X, y, X_train, X_test, y_train, y_test, y_test_economy_codes, y_test_population, y_test_region = check_etl()
    # check_data_info(X, y, X_train, X_test, y_train, y_test, show=False)

    # Train selected model(s)
    results_dt = train_and_evaluate_dt(X_train, y_train, X_test, y_test, model_type=model_type)

    test_results_df = X_test.copy()
    test_results_df["y_test"] = y_test.values

    for model_name, model_results in results_dt.items():
        model_name_formatted = model_name.lower().replace(" ", "_")
        test_results_df[f"y_pred_{model_name_formatted}"] = model_results["y_pred"]

    test_results_df["economy_code"] = y_test_economy_codes
    test_results_df["population"] = y_test_population
    test_results_df["regionwb"] = y_test_region


    # Just the selected models
    trained_models = {
        model_name.lower().replace(" ", "_"): model_results["model"]
        for model_name, model_results in results_dt.items()
    }

    metrics_df, feature_importance_df, metrics_list_by_cluster = ml_perf_eval_by_country(test_results_df, trained_models)
    def ensure_dataframe(results, label=""):
        if isinstance(results, pd.DataFrame):
            return results
        elif isinstance(results, dict):
            df = pd.DataFrame.from_dict(results, orient="index")
            return df
        elif isinstance(results, list):
            df = pd.DataFrame(results)
            return df
        else:
            print(f"⚠️ Warning: Unsupported format ({type(results)}) for {label}. Returning empty DataFrame.")
            return pd.DataFrame()
    

    metrics_df = ensure_dataframe(metrics_df, label="metrics_df")
    feature_importance_df = ensure_dataframe(feature_importance_df, label="feature_importance_df")
    metrics_list_by_cluster = ensure_dataframe(metrics_list_by_cluster, label="metrics_list_by_cluster")


    return metrics_df, feature_importance_df, metrics_list_by_cluster
