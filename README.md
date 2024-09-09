# sasta

This program helps users find the best grocery prices and deals from nearby supermarkets such as Albert Heijn, ALDI, Jumbo, Lidl, Dirk, and Toko. It aggregates prices from these supermarkets to help users get the best deals nearby.

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- Git
- Virtualenv
- Jupyter Notebook (for running web scrapers)

### Steps to Set Up the Environment

1. Clone the repository:

    ```bash
    git clone "https://github.com/venk12/sasta.git"
    ```

2. Navigate into the project directory:

    ```bash
    cd sasta
    ```

3. Create a virtual environment:

    ```bash
    virtualenv venv
    ```

4. Activate the virtual environment:

    - On Windows:
    
        ```bash
        venv\Scripts\activate
        ```

    - On MacOS/Linux:
    
        ```bash
        source venv/bin/activate
        ```

5. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

Once the repository is configured and all dependencies are installed, you can run the application using the following command:

```bash
streamlit run main.app
```

### Running the price scraping script

You can run the web scraping script (Jupyter Notebook) using the following command:

```bash
cd scraping
```

and opening the ah_listing.ipynb