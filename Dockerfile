# Use an official lightweight Python image
FROM python:3.9-slim
#RUN pip config set global.trusted-host "pypi.org files.pythonhosted.org pypi.python.org"
RUN python -m pip config set global.trusted-host=pypi.org files.pythonhosted.org
#RUN python3 -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --upgrade certifi
#RUN python3 -m pip install -U --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host http://files.pythonhosted.org pip==25.0
# Set the working directory inside the container
#RUN python -m pip install setuptools
WORKDIR /app

# Copy the app files into the container
COPY . .
#RUN python3 -m venv .venv
#RUN . .venv/bin/activate
# Install dependencies

RUN python -m pip install Flask
#RUN python3 -m pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org flask

# Command to run the app
CMD ["python", "app.py"]