# letterboxd-personal-recommender

This repo includes the AWS Lambda function for scraping logged film data from Letterboxd accounts as well as the UI and JS to process that data and do film comparisons.

The scraped data is stored in the browser's session storage so that it does not have to be re-fetched when re-run (which is only polite).
