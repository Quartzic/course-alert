# Course Alert

This Python script allows you to check the availability of seats in a specific course at Clemson University. It continuously checks the enrollment data for the specified course, and sends a push notification when a seat becomes available so that you can register as soon as possible.

## Prerequisites

To use this script, you'll need to have the following:

* Python 3 installed on your machine.
* `requests` library installed: `pip install requests`
* `beautifulsoup4` library installed: `pip install beautifulsoup4`
* A Pushover account (free trial available) and API Key: [https://pushover.net](https://pushover.net)

## Configuration

Before running the script, you need to make the following changes:

* Replace `INSERT_COOKIE_HERE` with the actual authentication cookie from iROAR. You can find this cookie by using your browser's developer tools to inspect a network request to Banner. Please note that this cookie may expire, so you may need to update it from time to time.

* Replace `INSERT_DATA_HERE` with the term and course reference number (CRN) for the course you want to monitor; for example, `term=202308&courseReferenceNumber=89433`.

* Set the `PUSHOVER_APP_KEY` and `PUSHOVER_USER_KEY` environment variables with your Pushover API key and User key respectively. You can obtain these keys from your Pushover account.

* (Optional) Adjust the `delay_between_checks` variable to set the delay (in seconds) between each check. The default value is 30 seconds. Making this value unreasonably low may result in trouble with the University, so please use this option with caution.

* (Optional) Adjust the `max_errors` variable to set the maximum number of errors allowed before the script stops. The default value is 5.

## Running the script

To run the script, simply execute it from the command line:

```bash
python course-alert.py
```

Once started, the script will continuously check the enrollment data for the specified course and send push notifications when seats become available. It will also send notifications in case of errors, or when the script is stopped.

## License

This script is provided under the MIT License. Please see the LICENSE file for more information.
