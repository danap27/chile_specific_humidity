import datetime
import os

import numpy as np


def monthly_mean(time_series, lat, lon):
    """
    Calcula el promedio mensual de una serie de tiempo. Considera únicamente años completos.
    Input:
        time_series: Serie de tiempo a la cual se le calculará el promedio mensual
        lat: Arreglo de latitudes
        lon: Arreglo de longitudes
    Output:
        monthly_mean: Promedio mensual de la serie de tiempo
    """
    complete_years = time_series.shape[0] // 12
    monthly_mean = np.mean(
        time_series[:complete_years*12].reshape(-1, 12, lat.shape[0], lon.shape[0]), axis=0)
    return monthly_mean


def monthly_regression(time_series):
    """
    Realiza un ajuste de regresión lineal periódica a una serie de tiempo.

    Argumentos:
    - time_series: Un array de forma (N,), donde N es el número de períodos en la serie de tiempo.

    Retorna:
    - adjusted_time_series : Un array de forma (N,), que representa la serie de tiempo ajustada mediante la regresión lineal periódica.
    """

    num_periods = time_series.shape[0]

    # Crea una matriz de predictores con características periódicas
    predictors = np.ones((num_periods, 5))
    time = np.arange(1, 13)
    predictors[:, 1] = np.cos(2 * np.pi * time / 12)
    predictors[:, 2] = np.sin(2 * np.pi * time / 12)
    predictors[:, 3] = np.cos(4 * np.pi * time / 12)
    predictors[:, 4] = np.sin(4 * np.pi * time / 12)

    # Realiza una regresión lineal periódica
    coefficients = np.linalg.lstsq(predictors, time_series, rcond=None)[0]

    # Calcula la serie de tiempo ajustada
    adjusted_time_series = np.matmul(predictors, coefficients)

    return adjusted_time_series


def monthly_anomaly_series(time_series, lat_series, lon_series):
    """
    Calcula la serie de anomalías de una serie de tiempo removiendo el ciclo estacional. Considera únicamente años completos.
    Input:
        time_series: Serie de tiempo a la cual se le calculará la serie de anomalías
        lat_series: Arreglo de latitudes
        lon_series: Arreglo de longitudes
    Output:
        monthly_anomaly_series: Serie de anomalías de la serie de tiempo
        series_monthly_mean_fit: Serie de tiempo ajustada mediante la regresión lineal periódica
        series_monthly_mean: Promedio mensual de la serie de tiempo
    """
    complete_years = time_series.shape[0] // 12
    series_monthly_mean = monthly_mean(time_series, lat_series, lon_series)
    serie_monthly_mean_fit_aux = np.zeros(series_monthly_mean.shape)
    for j in range(len(lon_series)):
        for i in range(len(lat_series)):
            serie_monthly_mean_fit_aux[:, i, j] = monthly_regression(
                series_monthly_mean[:, i, j])
    series_monthly_mean_fit = np.tile(
        serie_monthly_mean_fit_aux, (complete_years, 1, 1))
    monthly_anomaly_series = time_series - series_monthly_mean_fit
    return monthly_anomaly_series, series_monthly_mean_fit, series_monthly_mean


def init_models_dict(cordex_datasets):
    """
    Crea un diccionario con los modelos de CORDEX.
    Input:
        cordex_datasets: Lista de modelos de CORDEX
    Output:
        models_dict: Diccionario con los modelos de CORDEX
    """
    models_dict = {}
    content = {
        'anomaly_series': None,
        'monthly_mean_fit': None,
        'monthly_mean': None,
        'lat': None,
        'lon': None,
        'time': None,
        'huss': None,
        'model_id': None,
        'driving_model_id': None,
        'cordex_domain': None,
    }
    for model in cordex_datasets:
        model_name = model.model_id + '_' + \
            model.driving_model_id + '_' + model.CORDEX_domain
        models_dict[model_name] = content.copy()
    return models_dict


def percent_formatter(x, pos):
    """
    Formatea un número en porcentaje.
    """
    return '{:.2f}%'.format(x*100)

def kg2grams_formatter(x, pos):
    """
    Formatea un número en gramos.
    """
    return '{:.2f}'.format(x*1000)
    
def cfdate2datetime(cfdate_array):
    """
    Convierte un arreglo de fechas en formato CFDate a datetime.
    Input:
        cfdate_array: Arreglo de fechas en formato CFDate
    Output:
        datetime_array: Arreglo de fechas en formato datetime
    """
    return np.array([datetime.datetime.strptime(cfdate.isoformat(), '%Y-%m-%dT%H:%M:%S') for cfdate in cfdate_array])


def available_complementary_variables(root_path, experiment_category, primary_variable, complementary_variables):
    """
    Cuenta cuantas y cuales variables complementarias se encuentran disponibles para una variable primaria de cada modelo en particular.
    Input:
        root_path: Directorio raíz
        experiment_category: Categoría de experimento (historical, rcp85, etc.)
        primary_variable: Variable primaria (tas, pr, etc.)
        complementary_variables: Variables complementarias (lista)

    Output:
        dict_datasets: Diccionario con la cantidad de variables complementarias disponibles para la variable primaria de cada modelo en particular.
    """
    # Path de la variable primaria
    primary_variable_path = os.path.join(
        root_path, experiment_category, primary_variable)
    # Listamos los datasets de la variable primaria, solo carpetas
    primary_variable_datasets = [f for f in os.listdir(
        primary_variable_path) if os.path.isdir(os.path.join(primary_variable_path, f))]
    # El formato de las carpetas es el siguiente:
    # %s(variable)_%s(region)_%s(driving_model)_%s(experiment_type)_%s(ensemble)_%s(model_id)_%s(rcm_version)_%s(time_frequency)
    # Ejemplo: tas_EUR-11_CNRM-CERFACS-CNRM-CM5_historical_r1i1p1_CNRM-ALADIN63_v1_mon
    # Por lo tanto, removeremos el sufijo del nombre de la variable primaria para obtener sus otras características
    primary_variable_datasets = ['_'.join(primary_variable_dataset.split(
        '_')[1:-1]) for primary_variable_dataset in primary_variable_datasets]

    # Paths de las variables complementarias
    complementary_variables_path = [os.path.join(
        root_path, experiment_category, complementary_variable) for complementary_variable in complementary_variables]
    # Listamos los datasets de las variables complementarias, solo carpetas
    complementary_variables_datasets = [[f for f in os.listdir(complementary_variable_path) if os.path.isdir(
        os.path.join(complementary_variable_path, f))] for complementary_variable_path in complementary_variables_path]
    # Guardamos solo el nombre de la variable complementaria
    complementary_variables_name = [[complementary_variable_dataset.split(
        '_')[0] for complementary_variable_dataset in complementary_variable_datasets] for complementary_variable_datasets in complementary_variables_datasets]
    # El formato de las carpetas es el mismo que el de la variable primaria, por lo tanto, removeremos el sufijo del nombre de la variable para obtener sus otras características
    complementary_variables_datasets = [['_'.join(complementary_variable_dataset.split(
        '_')[1:-1]) for complementary_variable_dataset in complementary_variable_datasets] for complementary_variable_datasets in complementary_variables_datasets]

    dict_datasets = {}

    for primary_variable_dataset in primary_variable_datasets:
        count = 0
        names = []
        for i, complementary_variable in enumerate(complementary_variables_datasets):
            if primary_variable_dataset in complementary_variable:
                count += 1
                names.append(complementary_variables_name[i][0])
        # Create key of count if it doesn't exist
        if count not in dict_datasets:
            dict_datasets[count] = []

        dict_datasets[count].append((primary_variable_dataset, names))

    return dict_datasets
