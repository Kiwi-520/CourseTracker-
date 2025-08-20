# Course Tracker Application

## Overview
The Course Tracker application is a dynamic and responsive web application built using Streamlit. It allows users to track their learning progress across various courses and subcourses, providing real-time updates and visualizations of their achievements.

## Features
- **User-Friendly Interface**: Intuitive design for easy navigation and interaction.
- **Real-Time Updates**: Changes are reflected immediately in the UI.
- **Database Integration**: Utilizes MongoDB for storing course and user data.
- **Dynamic Components**: Modular components for sidebar, dashboard, and course views.
- **Progress Tracking**: Visual representations of course completion and metrics.

## Project Structure
```
course-tracker-app
├── src
│   ├── app.py
│   ├── database
│   │   ├── __init__.py
│   │   ├── mongodb_client.py
│   │   └── models.py
│   ├── components
│   │   ├── __init__.py
│   │   ├── sidebar.py
│   │   ├── dashboard.py
│   │   ├── course_view.py
│   │   └── metrics.py
│   ├── utils
│   │   ├── __init__.py
│   │   ├── helpers.py
│   │   └── constants.py
│   └── styles
│       ├── __init__.py
│       ├── main.css
│       └── components.css
├── config
│   ├── __init__.py
│   ├── settings.py
│   └── database.py
├── tests
│   ├── __init__.py
│   ├── test_database.py
│   ├── test_components.py
│   └── test_utils.py
├── data
│   └── sample_courses.json
├── requirements.txt
├── .env.example
├── .gitignore
├── docker-compose.yml
└── Dockerfile
```

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   cd course-tracker-app
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up your environment variables by copying `.env.example` to `.env` and filling in the necessary details.

## Usage
To run the application, execute the following command:
```
streamlit run src/app.py
```

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.