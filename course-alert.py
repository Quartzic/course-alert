import requests
from bs4 import BeautifulSoup
import time
import os
import atexit

PUSHOVER_APP_KEY = os.getenv("PUSHOVER_APP_KEY")
PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER_KEY")

url = "https://regssb.sis.clemson.edu/StudentRegistrationSsb/ssb/searchResults/getEnrollmentInfo"

# Define the headers (replace with actual headers, including auth cookie if needed)
headers = {
    "Cookie": "INSERT_COOKIE_HERE",
    'Content-Type': 'application/x-www-form-urlencoded'
}

# The data is the term and course reference number
data = "INSERT_DATA_HERE"

# Define the delay between checks in seconds
delay_between_checks = 30

# Max errors before stopping the script
max_errors = 5

def send_notification(message, title):
    # Send a push notification using the Pushover API
    try:
        requests.post("https://api.pushover.net/1/messages.json", data={
            "token": PUSHOVER_APP_KEY,
            "user": PUSHOVER_USER_KEY,
            "message": message,
            "title": f"Course Alert: {title}"
        })
    except:
        pass

def check_enrollment():
        print("Checking enrollment at " + time.strftime("%H:%M:%S", time.localtime()))

        # Make a network request to get enrollment data
        response = requests.post(url, data=data, headers=headers)
        response.raise_for_status()

        # Parse the HTML response
        soup = BeautifulSoup(response.text, 'html.parser')
        section = soup.find('section', attrs={'aria-labelledby': 'enrollmentInfo'})
        if section is None:
            raise Exception("Unable to parse response")

        # Extract enrollment data
        enrollment_actual = int(section.find_all('span', attrs={'dir': 'ltr'})[0].text)
        enrollment_maximum = int(section.find_all('span', attrs={'dir': 'ltr'})[1].text)
        enrollment_seats_available = int(section.find_all('span', attrs={'dir': 'ltr'})[2].text)

        if(enrollment_seats_available > 0):
            # If the course is open, send a push notification
            send_notification(f"Enrollment Actual: {enrollment_actual}\n"
                                f"Enrollment Maximum: {enrollment_maximum}\n"
                                f"Enrollment Seats Available: {enrollment_seats_available}",
                                title="Course is open!")
        else:
            print(f"Course is not open, trying again in {delay_between_checks} seconds...")


def exit_handler():
    print("Exiting...")
    send_notification("The script has stopped.", title="Script stopped")

# Continuously check enrollment every 30 seconds
def main():
    error_count = 0
    atexit.register(exit_handler)
    
    while True:
        try:
            check_enrollment()
            error_count = 0 # Reset error count if the check was successful

        except Exception as e:
            error_count+=1
            
            if(error_count > max_errors):
                send_notification("The script encountered too many errors and will stop.", title="Too many errors")
                exit()
            else:
                send_notification(f"Error {error_count}/{max_errors}: {e}", title="Error checking enrollment")

        
        time.sleep(delay_between_checks)

if(__name__ == "__main__"):
    main()