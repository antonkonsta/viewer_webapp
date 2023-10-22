import tkinter as tk
from tkinter import filedialog, simpledialog, IntVar, ttk
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np 
import os

def get_payload_mass():
    global payload_mass
    payload_mass = simpledialog.askfloat("Input", "Enter the mass of the payload (kg):")
    if payload_mass is not None:
        print(f"Payload mass set to {payload_mass} kg")

# Create a function to open and process the CSV file
def open_csv_file():
    global df
    # Open a file dialog to select the CSV file
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])

    if file_path:
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
            'altitude': float,
        }

        # Read the CSV file with specified data types
        df = pd.read_csv(file_path, dtype=data_types)

        # Convert milliseconds to seconds
        df['seconds'] = df['milliseconds'] / 1000.0


def plot_selected_data():
    if df is not None:
        plt.figure(figsize=(10, 6))
        
        if acceleration_var.get():
            df['acceleration_magnitude'] = np.sqrt(df['linAccelerationx']**2 + df['linAccelerationy']**2 + df['linAccelerationz']**2)
            plt.plot(df['seconds'], df['acceleration_magnitude'], label='Acceleration Magnitude', color='blue')
      
        '''if angular_velocity_var.get():
            df['angular_velocity_magnitude'] = np.sqrt(df['angVelocityx']**2 + df['angVelocityy']**2 + df['angVelocityz']**2)
            plt.plot(df['seconds'], df['angular_velocity_magnitude'], label='Angular Velocity Magnitude', color='green')'''
        if g_force_var.get():
            if 'acceleration_magnitude' not in df:
                df['acceleration_magnitude'] = np.sqrt(df['accelerationx']**2 + df['accelerationy']**2 + df['accelerationz']**2)
            df['g_force'] = df['acceleration_magnitude'] / 9.81
            plt.plot(df['seconds'], df['g_force'], label='G-Force', color='red')

        if velocity_var.get():
            df['velocity_magnitude'] = np.sqrt(df['orientationx']**2 + df['orientationy']**2 + df['orientationz']**2)
            plt.plot(df['seconds'], df['velocity_magnitude'], label='Velocity Magnitude', color='purple')
      
        plt.xlabel('Seconds')
        plt.legend()
        plt.grid(True)
        plt.show()

# Create the main application window
app = tk.Tk()
app.title('CSV Data Processor')
app.configure(bg='#00703c')
image_path = os.path.join(os.path.dirname(__file__), "logo.png")

# Load the image
image = tk.PhotoImage(file=image_path)
image = image.subsample(14, 14)  # Reduces the size to half (adjust the factors as needed)
image_label = tk.Label(app, image=image, bg='#00703c')
image_label.pack()


open_button = tk.Button(app, text='Open CSV File', command=open_csv_file, bg='#a7a177', fg='black')
open_button.pack(pady=10)

# Toggle buttons for data selection
acceleration_var = IntVar()
acceleration_check = tk.Checkbutton(app, text="Acceleration", variable=acceleration_var, bg='#a7a177', fg='black')
acceleration_check.pack(pady=5)
'''
angular_velocity_var = IntVar()
angular_velocity_check = tk.Checkbutton(app, text="Angular Velocity", variable=angular_velocity_var) 
angular_velocity_check.pack(pady=5)
'''
g_force_var = IntVar()
g_force_check = tk.Checkbutton(app, text="G-Force", variable=g_force_var, bg='#a7a177', fg='black')
g_force_check.pack(pady=5)

velocity_var = IntVar()
velocity_check = tk.Checkbutton(app, text="Velocity", variable=velocity_var, bg='#a7a177', fg='black')

velocity_check.pack(pady=5)

# One plot button for plotting selected data
plot_button = tk.Button(app, text='Plot Selected Data', command=plot_selected_data, bg='#a7a177', fg='black')
plot_button.pack(pady=10)

#mass_button = tk.Button(app, text='Enter Payload Mass', command=get_payload_mass)
#mass_button.pack(pady=10)

app.mainloop()