# Ethylene Simulation Inside Avocado Package - Web Application

APP link: https://ethylene-simulator-in-package-f855cb754629.herokuapp.com/ 


This project is a web-based adaptation of the scientific model developed by **Dr. Akshay Sonawane** at ATB Potsdam to simulate gas concentrations in modified atmosphere packaging (MAP) for avocados. It converts the original `tkinter` desktop application into a user-friendly web interface that can run locally on your machine. This web app can also be easily published on AWS Elastic Beanstalk (EB) with all the required files located in the ethylene-avocado-webapp.

The application predicts the concentration of **ethylene (C₂H₄)**, **oxygen (O₂)**, and **carbon dioxide (CO₂)** inside an avocado package over a defined storage period, considering parameters such as fruit mass, temperature, package perforations, and the presence of an ethylene scavenger.

This work is based on the model published in *Postharvest Biology and Technology*:

> Sonawane et al (2024). A model integrating fruit physiology, perforation, and scavenger for prediction of ethylene accumulation in fruit packages. *Postharvest Biology and Technology, 209*, 112734.
> [https://doi.org/10.1016/j.postharvbio.2023.112734](https://doi.org/10.1016/j.postharvbio.2023.112734)

---

## Prerequisites

* Python 3.7 or newer
* A modern web browser (Chrome, Firefox, Edge, etc.)

---

## File Structure

├── app.py
├── calculations.py
├── requirements.txt
├── Procfile
├── templates/
│   ├── base.html
│   └── index.html
└── static/
    ├── css/
    │   └── style.css
    ├── js/
    │   └── script.js
    └── img/
        ├── logo.svg
        └── avocado.svg

## Installation

1. **Navigate to the project directory:**

   ```sh
   cd C:\....\.....\.....\......\ethylene-avocado-webapp
   ```

2. **Create and activate a Python virtual environment (recommended):**

   ```sh
   # For Windows
   python -m venv venv
   venv\Scripts\activate

   # For macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install the required packages:**

   ```sh
   pip install -r requirements.txt
   ```

   **requirements.txt:**

   ```
   Flask==3.0.3
   numpy==1.26.4
   matplotlib==3.8.4
   Pillow==10.3.0
   ```

---

## Running the Application

1. Ensure you are in the project directory and your virtual environment is activated.

2. Run the Flask application:

   ```sh
   python app.py
   ```

3. The terminal will indicate that the server is running, typically on `http://127.0.0.1:5000`.

4. Open your browser and navigate to:

   [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## Using the Web Application

1. The page loads with default values in the **Input Parameters** form.
2. Adjust the input parameters (e.g., fruit mass, temperature, storage time) according to your simulation needs.
3. Click the **"Update Plots"** button to run the simulation.
4. The graphs display the predicted gas concentrations over the selected storage period.
5. If an input is outside the model’s valid range, a warning message will appear below the form.
6. Click **"Reset"** to clear all inputs and reset the plots.

---

## License


This project is for educational and research purposes. Please cite the original publication if you use the model in your work.



