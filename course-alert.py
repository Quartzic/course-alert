import requests
from bs4 import BeautifulSoup
import time
import os
import atexit

PUSHOVER_APP_KEY = os.getenv("PUSHOVER_APP_KEY")
PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER_KEY")

url = "https://regssb.sis.clemson.edu/StudentRegistrationSsb/ssb/searchResults/getEnrollmentInfo"

# Replace this with your actual Clemson cookie after logging in
headers = {
    "Cookie": "YOUR-CLEMSON-COOKIE-HERE",
    "Content-Type": "application/x-www-form-urlencoded",
}

# Update this based on the term you're trying to enroll in
term = "202308"

# Update this based on the courses you're trying to enroll in
courses_to_check = [
    {"crn": "89433", "title": "Reading Video Games"},
    {"crn": "89176", "title": "Linear Algebra"},
]

# Define the delay between checks in seconds
delay_between_checks = 30

# Max errors before stopping the script
max_errors = 5


def send_notification(message, title, user_key=PUSHOVER_USER_KEY):
    # Send a push notification using the Pushover API
    try:
        print(f"Sending push notification ({title}): {message}) to {user_key}")
        response = requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token": PUSHOVER_APP_KEY,
                "user": user_key,
                "message": message,
                "title": f"Course Alert: {title}",
            },
        )
        response.raise_for_status()

    except:
        print(f"Unable to send push notification: {title} - {message}")
        pass


def check_enrollment():
    print("Checking enrollment at " + time.strftime("%H:%M:%S", time.localtime()))

    for course in courses_to_check:
        print(f"Checking {course['title']}...")

        # Make a network request to get enrollment data
        response = requests.post(
            url,
            data=f"term={term}&courseReferenceNumber={course['crn']}",
            headers=headers,
        )
        response.raise_for_status()

        # Parse the HTML response
        soup = BeautifulSoup(response.text, "html.parser")
        section = soup.find("section", attrs={"aria-labelledby": "enrollmentInfo"})
        if section is None:
            raise Exception("Unable to parse response")

        # Extract enrollment data
        enrollment_actual = int(section.find_all("span", attrs={"dir": "ltr"})[0].text)
        enrollment_maximum = int(section.find_all("span", attrs={"dir": "ltr"})[1].text)
        enrollment_seats_available = int(
            section.find_all("span", attrs={"dir": "ltr"})[2].text
        )

        if enrollment_seats_available > 0:
            # If the course is open, send a push notification
            if "user_key" in course:
                send_notification(
                    f"Enrollment Actual: {enrollment_actual}\n"
                    f"Enrollment Maximum: {enrollment_maximum}\n"
                    f"Enrollment Seats Available: {enrollment_seats_available}",
                    title=f"{course['title']} is open!",
                    user_key=course['user_key'],
                )
            else:
                send_notification(
                    f"Enrollment Actual: {enrollment_actual}\n"
                    f"Enrollment Maximum: {enrollment_maximum}\n"
                    f"Enrollment Seats Available: {enrollment_seats_available}",
                    title=f"{course['title']} is open!",
                )
        else:
            print(
                f"{course['title']} is not open, trying again in {delay_between_checks} seconds..."
            )


def exit_handler():
    print("Exiting...")
    send_notification("The service has stopped.", title="Course Alert stopped")


# Continuously check enrollment every 30 seconds
def main():
    error_count = 0
    atexit.register(exit_handler)

    send_notification("The service has started.", title="Course Alert started")
    print(
        "Check to make sure you got a notification from Pushover before continuing. If you didn't, check your Pushover app key and user key."
    )

    while True:
        try:
            check_enrollment()
            error_count = 0  # Reset error count if the check was successful

        except Exception as e:
            error_count += 1

            if error_count > max_errors:
                send_notification(
                    "The script encountered too many errors and will stop.",
                    title="Too many errors",
                )
                exit()
            else:
                send_notification(
                    f"Error {error_count}/{max_errors}: {e}",
                    title="Error checking enrollment",
                )

        time.sleep(delay_between_checks)


if __name__ == "__main__":
    main()
