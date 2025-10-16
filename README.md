# 🌐 Ethylene Simulation Inside Avocado Package - Web Application 🚀

**Live App:** [https://ethylene-simulator-in-package-f855cb754629.herokuapp.com/](https://ethylene-simulator-in-package-f855cb754629.herokuapp.com/)

This project is a web-based adaptation of the scientific model developed by **Dr. Akshay Sonawane** at ATB Potsdam to simulate gas concentrations in modified atmosphere packaging (MAP) for avocados. It converts the original `tkinter` desktop application into a user-friendly web interface that can run locally or be deployed on AWS Elastic Beanstalk.

The application predicts the concentration of **ethylene (C₂H₄)**, **oxygen (O₂)**, and **carbon dioxide (CO₂)** inside an avocado package over a defined storage period, considering parameters such as fruit mass, temperature, package perforations, and the presence of an ethylene scavenger.

This work is based on the model published in *Postharvest Biology and Technology*:

> Sonawane et al (2024). A model integrating fruit physiology, perforation, and scavenger for prediction of ethylene accumulation in fruit packages. *Postharvest Biology and Technology, 209*, 112734.
> [https://doi.org/10.1016/j.postharvbio.2023.112734](https://doi.org/10.1016/j.postharvbio.2023.112734)

---

## ⚙️ Project History

Originally developed in **Matlab**, then converted to **Python** with a GUI, and finally adapted as a **web application** for easier use and visualization.

**Screenshots & Graphics:**

![Web App Main Screen](static/img/avocado.svg)
*Main interface of the web application.*

![Gas Concentration Graph](static/img/graph_example.png)
*Predicted gas concentrations over time.*

![Workflow Diagram](static/img/workflow.png)
*Workflow diagram showing input, simulation, and output.*

---

## 🌐 Prerequisites

* Python 3.7 or newer
* Modern web browser (Chrome, Firefox, Edge, etc.)

---

## 📂 File Structure

```
ethylene-avocado-webapp/
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
        ├── avocado.svg
        ├── graph_example.png
        └── workflow.png
```

---

## ⚙️ Installation

1. **Navigate to the project directory:**

```sh
cd C:\path\to\ethylene-avocado-webapp
```

2. **Create and activate a Python virtual environment:**

```sh
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install the required packages:**

```sh
pip install -r requirements.txt
```

**Example `requirements.txt` content:**

```
Flask==3.0.3
numpy==1.26.4
matplotlib==3.8.4
Pillow==10.3.0
```

---

## 🚀 Running the Application

1. Ensure your virtual environment is activated.
2. Run the Flask server:

```sh
python app.py
```

3. Open your browser and navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## ⚙️ Using the Web Application

1. Adjust the **Input Parameters** form (fruit mass, temperature, storage time, etc.).
2. Click **"Update Plots"** to run the simulation.
3. Graphs display predicted ethylene, oxygen, and carbon dioxide concentrations.

**Example Graph:**

![Gas Concentration Over Time](static/img/graph_example.png)

4. Warnings appear if input parameters are outside the valid model range.
5. Use **"Reset"** to clear inputs and plots.

**Visual Guide:**

![Step-by-step Instructions](static/img/steps.png)
*Graphical guide to using the application.*

---

## 📄 License

This project is intended for **educational and research purposes**. Please cite the original publication if using the model.
