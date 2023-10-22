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
    color_gforce = request.form.get('color_gforce', '#ff0000')  # Default to red if no color selected
    color_velocity = request.form.get('color_velocity', '#00ff00')  # Default to green
    color_altitude = request.form.get('color_altitude', '#0000ff')  # Default to blue
    color_lin_acceleration = request.form.get('color_lin_acceleration', '#ffa500')  # Default to yellow
    color_acceleration = request.form.get('color_acceleration', '#FC0FC0')  # Default to pink
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
    plot_altitude = 'plot_altitude' in request.form 
    plot_radial_gforce = 'plot_radial_gforce' in request.form  # Added checkbox for radial g-force
    compare = 'compare' in request.form
    plot_lin_acceleration = 'plot_lin_acceleration' in request.form 
    plot_acceleration = 'plot_acceleration' in request.form 


    

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
        'altitude' : float,
    }

    # Read the CSV file with specified data types
    df = pd.read_csv(file_path, dtype=data_types)

    # Convert milliseconds to seconds
    df['seconds'] = df['milliseconds'] / 1000.0

    return redirect(url_for('plot_data', 
                            plot_gforce=plot_gforce, 
                            plot_velocity=plot_velocity, 
                            plot_altitude=plot_altitude, 
                            color_gforce=color_gforce, 
                            color_velocity=color_velocity, 
                            color_altitude=color_altitude,
                            compare=compare,
                            plot_lin_acceleration = plot_lin_acceleration,
                            color_lin_acceleration = color_lin_acceleration,
                            plot_acceleration = plot_acceleration,
                            color_acceleration = color_acceleration))


@app.route('/plot_data')
def plot_data():
    global df
    color_gforce = request.args.get('color_gforce', '#ff0000')
    color_velocity = request.args.get('color_velocity', '#00ff00')
    color_altitude = request.args.get('color_altitude', '#0000ff')
    color_lin_acceleration = request.args.get('color_lin_acceleration', '#ffa500')
    color_acceleration = request.args.get('color_acceleration', '#FC0FC0')
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

        if 'radial_gforce' not in df:  # Added radial g-force calculation
            angular_velocity = np.sqrt(df['angVelocityx']**2 + df['angVelocityy']**2 + df['angVelocityz']**2)
            radius = 0.025  # You may need to adjust this based on your specific application
            centripetal_acceleration = angular_velocity**2 * radius
            df['radial_gforce'] = centripetal_acceleration / 9.8

        if 'lin_acceleration_magnitude' not in df:
            df['lin_acceleration_magnitude'] = np.sqrt(df['linAccelerationx']**2 + df['linAccelerationy']**2 + df['linAccelerationz']**2)

        if 'acceleration_magnitude' not in df:
            df['acceleration_magnitude'] = np.sqrt(df['accelerationx']**2 + df['accelerationy']**2 + df['accelerationz']**2)
        
        
        plot_lin_acceleration = request.args.get('plot_lin_acceleration', default='off')

        plot_acceleration = request.args.get('plot_acceleration', default='off')

        # Check if the "Plot G-Force" checkbox is selected
        plot_gforce = request.args.get('plot_gforce', default='off')
        # Check if the "Plot Velocity" checkbox is selected
        plot_velocity = request.args.get('plot_velocity', default='off')

        plot_altitude = request.args.get('plot_altitude', default='off')

        plot_radial_gforce = request.args.get('plot_radial_gforce', default='off')  # Added radial g-force



        # Create a Plotly figure with both G-Force and Velocity
        fig = px.line(labels={'g_force': 'G-Force', 'velocity': 'Velocity'})

        # Customize the figure (add titles, labels, etc. if needed)
        fig.update_layout(
            title="Plot",
            xaxis_title="Seconds",
            yaxis_title="Values",
        )

        total_height = 680  # Adjust as needed
        num_plots = sum([plot_gforce == 'True', plot_velocity == 'True', 
                        plot_altitude == 'True', plot_radial_gforce == 'True', 
                        plot_lin_acceleration == 'True', plot_acceleration == 'True'])
        plot_height = total_height // max(1, num_plots) if num_plots else total_height

        # Add both G-Force and Velocity to the figure if the checkboxes are selected
        compare = request.args.get('compare', default='off') == 'True'
        if compare:
            plots = []
            if plot_gforce == 'True':
                fig = px.line(df, x='seconds', y='g_force', labels={'g_force': 'G-Force'})
                fig.update_layout(title="G-Force", xaxis_title="Seconds", yaxis_title="G-Force",
                                  height=plot_height)  # Adjust height here
                fig.data[0].line.color = color_gforce
                plots.append(fig.to_html(full_html=False))

            if plot_velocity == 'True':
                fig = px.line(df, x='seconds', y='velocity', labels={'velocity': 'Velocity'})
                fig.update_layout(title="Velocity", xaxis_title="Seconds", yaxis_title="Velocity",
                                  height=plot_height)  # Adjust height here
                fig.data[0].line.color = color_velocity
                plots.append(fig.to_html(full_html=False))

            if plot_altitude == 'True':
                fig = px.line(df, x='seconds', y='altitude', labels={'altitude': 'Altitude'})
                fig.update_layout(title="Altitude", xaxis_title="Seconds", yaxis_title="Altitude",
                                  height=plot_height)  # Adjust height here
                fig.data[0].line.color = color_altitude
                plots.append(fig.to_html(full_html=False))

            if plot_lin_acceleration == 'True':
                fig = px.line(df, x='seconds', y='lin_acceleration_magnitude', labels={'lin_acceleration_magnitude': 'Linear Acceleration'})
                fig.update_layout(title="Linear Acceleration", xaxis_title="Seconds", yaxis_title="Linear Acceleration",
                                  height=plot_height)  # Adjust height here
                fig.data[0].line.color = color_lin_acceleration
                plots.append(fig.to_html(full_html=False))

            if plot_acceleration == 'True':
                fig = px.line(df, x='seconds', y='acceleration_magnitude', labels={'acceleration_magnitude': 'Acceleration'})
                fig.update_layout(title="Acceleration", xaxis_title="Seconds", yaxis_title="Acceleration",
                                  height=plot_height)  # Adjust height here
                fig.data[0].line.color = color_acceleration
                plots.append(fig.to_html(full_html=False))

            # ... (add similar code for other plots)

            return ''.join(plots)
        else:
            if plot_gforce == 'True':
                trace = px.line(df, x='seconds', y='g_force').data[0]
                trace.line.color = color_gforce  # Modify the trace color here
                fig.add_trace(trace) 

            if plot_velocity == 'True':
                trace = px.line(df, x='seconds', y='velocity').data[0]
                trace.line.color = color_velocity  # Modify the trace color here
                fig.add_trace(trace)

            if plot_altitude == 'True':
                trace = px.line(df, x='seconds', y='altitude').data[0]
                trace.line.color = color_altitude  # Modify the trace color here
                fig.add_trace(trace)


            if plot_radial_gforce == 'True':  # Added radial g-force plot
                fig.add_trace(px.line(df, x='seconds', y='radial_gforce').data[0])
            # Convert the figure to HTML and serve it

            if plot_lin_acceleration == 'True':
                trace = px.line(df, x='seconds', y='lin_acceleration_magnitude').data[0]
                trace.line.color = color_lin_acceleration  # Modify the trace color here
                fig.add_trace(trace)

            if plot_acceleration == 'True':
                trace = px.line(df, x='seconds', y='acceleration_magnitude').data[0]
                trace.line.color = color_acceleration  # Modify the trace color here
                fig.add_trace(trace)

            plot_div = fig.to_html(full_html=False)

            return plot_div

    return "No data to plot."

if __name__ == '__main__':
    app.run()
