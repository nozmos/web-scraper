FROM python:3.9

# INSTALLING CHROME
# Add trusting keys for apt to repositories
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
# Add Google Chrome
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
# Update apt
RUN apt-get -y update
# Finally install Chrome
RUN apt-get install -y google-chrome-stable

# INSTALLING CHROMEDRIVER
# Download the ChromeDriver zip file
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
# Unzip ChromeDriver
RUN apt-get install -yqq unzip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# Copy everything
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Run the program
CMD ["python", "main.py"]