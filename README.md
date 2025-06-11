Build a Python Flask web app using Object-Oriented Programming. The app should:

1. Fetch active CoinDCX futures trading pairs from this endpoint:
   - https://api.coindcx.com/exchange/v1/derivatives/futures/data/active_instruments

2. For each pair, fetch its details from:
   - https://api.coindcx.com/exchange/v1/derivatives/futures/data/instrument?pair=<PAIR_NAME>

3. Use SQLAlchemy ORM and SQLite to store the data in a `futures_pairs` table with fields:
   - pair (string, primary key)
   - kind (string)
   - status (string)
   - tick_size (float)
   - price_band_upper (string)

4. Use OOP structure:
   - Separate class for API client (`CoinDCXClient`)
   - SQLAlchemy model for the DB table (`FuturesPair`)
   - Route `/refresh` to fetch and store data
   - Route `/` to display the stored futures data in a table

5. Use Jinja2 templates for rendering
6. Style the UI with Tailwind CSS using CDN
7. Limit display to top 20 results for performance
8. Include a “Refresh Data” link on the UI

Output the project as:
- `app.py` for Flask logic
- `models.py` for DB models
- `coindcx.py` for the API class
- `templates/futures.html` for the UI
