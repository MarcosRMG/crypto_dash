import pandas as pd
from autots import AutoTS
import streamlit as st


@st.cache_data
def auto_ts_forecast(df: pd.DataFrame, value_col: str, transformer_list: list[str],
                     model_list: list[str], exceptin_msg: str, date_col: str=None, forecast_length=1, frequency='QE'):
    model = AutoTS(
        forecast_length=forecast_length,
        frequency=frequency,
        prediction_interval=0.9,
        ensemble=model_list,
        model_list=model_list,
        transformer_list=transformer_list,
        drop_most_recent=0, 
        max_generations=2,
        num_validations=1,
        validation_method='backward',
        verbose=False
    )

    try:
        model = model.fit(
            df,
            date_col=date_col,
            value_col=value_col,
        )
    except ValueError:
        st.write(exceptin_msg)

    return model
