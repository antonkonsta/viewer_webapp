from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import numpy as np
import os
import plotly.express as px

app = Flask(__name__)

# Initialize global variables
payload_mass = None
df = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    global df
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)

    # Save and process the uploaded CSV file
    file_path = os.path.join("uploads", file.filename)
    file.save(file_path)

    # Check if the "Plot G-Force" checkbox is selected
    plot_gforce = 'plot_gforce' in request.form
    plot_velocity = 'plot_velocity' in request.form 
    print("\n -- Checkbox: ", plot_velocity, "\n")

    # Define a dictionary to map column names to data types
    data_types = {
        'milliseconds': int,
        'orientationx': float,
        'orientationy': float,
        'orientationz': float,
        'angVelocityx': float,
        'angVelocityy': float,
        'angVelocityz': float,
        'linAccelerationx': float,
        'linAccelerationy': float,
        'linAccelerationz': float,
        'magneticx': float,
        'magneticy': float,
        'magneticz': float,
        'accelerationx': float,
        'accelerationy': float,
        'accelerationz': float,
        'gravityx': float,
        'gravityy': float,
        'gravityz': float,
    }

    # Read the CSV file with specified data types
    df = pd.read_csv(file_path, dtype=data_types)

    # Convert milliseconds to seconds
    df['seconds'] = df['milliseconds'] / 1000.0

    return redirect(url_for('plot_data', plot_gforce=plot_gforce, plot_velocity=plot_velocity))

@app.route('/plot_data')
def plot_data():
    global df
    if df is not None:
        # Check if 'g_force' column exists, and calculate it if not
        if 'g_force' not in df:
            if 'acceleration_magnitude' not in df:
                df['acceleration_magnitude'] = np.sqrt(df['accelerationx']**2 + df['accelerationy']**2 + df['accelerationz']**2)
            df['g_force'] = df['acceleration_magnitude'] / 9.8

        # Check if 'velocity' column exists, and calculate it if not
        if 'velocity' not in df:
            df['velocity_x'] = np.cumsum(df['linAccelerationx']) * (df['milliseconds'].diff() / 1000.0).fillna(0)
            df['velocity_y'] = np.cumsum(df['linAccelerationy']) * (df['milliseconds'].diff() / 1000.0).fillna(0)
            df['velocity_z'] = np.cumsum(df['linAccelerationz']) * (df['milliseconds'].diff() / 1000.0).fillna(0)
            df['velocity'] = np.sqrt(df['velocity_x']**2 + df['velocity_y']**2 + df['velocity_z']**2)

        # Check if the "Plot G-Force" checkbox is selected
        plot_gforce = request.args.get('plot_gforce', default='off')
        # Check if the "Plot Velocity" checkbox is selected
        plot_velocity = request.args.get('plot_velocity', default='off')

        # Create a Plotly figure with both G-Force and Velocity
        fig = px.line(labels={'g_force': 'G-Force', 'velocity': 'Velocity'})

        # Customize the figure (add titles, labels, etc. if needed)
        fig.update_layout(
            title="Interactive G-Force and Velocity Plot",
            xaxis_title="Seconds",
            yaxis_title="Values",
        )

        # Add both G-Force and Velocity to the figure if the checkboxes are selected
        if plot_gforce == 'True':
            fig.add_trace(px.line(df, x='seconds', y='g_force').data[0])

        if plot_velocity == 'True':
            fig.add_trace(px.line(df, x='seconds', y='velocity').data[0])

        # Convert the figure to HTML and serve it
        plot_div = fig.to_html(full_html=False)

        return plot_div

    return "No data to plot."


if __name__ == '__main__':
    app.run()
