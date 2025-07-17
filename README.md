# Prestamos Laboratorios Industrial

## Overview

The **Prestamos Laboratorios Industrial** project is an application designed to manage and facilitate the loaning of industrial production laboratory equipment, resources and rooms. It provides functionality for managing inventory, resources, and user interactions within a laboratory environment.The application centralizes the entire process, from request and approval to tracking and return, eliminating reliance on manual records. By offering an intuitive interface and a robust database for data persistence, this solution optimizes operational efficiency, minimizes reservation errors, and provides complete traceability of resource usage, significantly improving the administration of valuable assets.

## Project Structure

This repository contains the following components:

### Files:
- **app_with_reload.py**: Execute the main application script including live reloading and logging features.
- **main.py**: Entry point for the application logic.
- **version_info.txt**: Contains versioning information about the project.
- **requirements.txt**: Lists the dependencies required to run the project.
- **uso_de_espacios.spec**: Configuration file to package and deploy the app.

### Directories:
- **assets/**: Contains app and button icons.
- **database/**: Includes database-related files (schemas, models, etc.).
- **utils/**: Utility functions and helper scripts for the application.
- **views/**: Contains view templates for the application’s user interface.

## Using a Virtual Environment (Recommended)

It is recommended to use a virtual environment to isolate the project's dependencies and avoid conflicts with other Python projects. You can create and activate a virtual environment with the following steps:

**On Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**On Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

---

## Installation

To set up and run this project locally, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ItsFranco666/Prestamos_Laboratorios_Industrial.git
   ```
2. **Navigate to the project directory:**

   ```bash
   cd Prestamos_Laboratorios_Industrial
   ```
3. **Install dependencies:**

   Run the following command to install all dependencies listed in the `requirements.txt` file:

   ```bash
   pip install -r requirements.txt
   ```

   This will automatically install all the libraries required for the project to work.

4. **Run the application:**

   You can start the application by running:

   ```bash
   python main.py
   ```

   If you want to use the reloading feature, run:

   ```bash
   python app_with_reload.py
   ```

## Features

- **User Management**: Ability to create, manage, and authenticate users.
- **Inventory Management**: Manage the rooms and resources available in the laboratories.
- **Loan System**: Loaning and returning equipment to/from users.
- **Dashboard**: View loan statistics, available resources, and more.

## Requirements

- Python 3.x
- Dependencies as listed in `requirements.txt`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For more information or issues, please contact the repository owner or raise an issue in the repository.