import os
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, flash
from flask_cors import CORS
from models import Session, FuturesPair
from coindcx import CoinDCXClient
import logging
from werkzeug.middleware.proxy_fix import ProxyFix

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure app
app.wsgi_app = ProxyFix(app.wsgi_app)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure CORS
CORS(app, resources={
    r"/*": {
        "origins": os.getenv('CORS_ORIGINS', '*').split(','),
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

client = CoinDCXClient()

@app.route('/')
def index():
    session = Session()
    try:
        # Get top 20 pairs ordered by pair name
        pairs = session.query(FuturesPair).order_by(FuturesPair.pair).limit(20).all()
        return render_template('futures.html', pairs=pairs)
    finally:
        session.close()

@app.route('/refresh')
def refresh():
    session = Session()
    try:
        # Clear existing data
        session.query(FuturesPair).delete()
        
        # Fetch active pairs
        active_pairs = client.get_active_pairs()
        logger.info(f"Retrieved {len(active_pairs)} active pairs")
        
        # Log the type and structure of active_pairs for debugging
        logger.debug(f"Active pairs type: {type(active_pairs)}, Content: {active_pairs[:2]}")
        
        # Fetch details for each pair and store in database
        for pair_data in active_pairs:
            # Handle both string and dictionary responses
            pair_name = pair_data.get('pair') if isinstance(pair_data, dict) else str(pair_data)
            
            try:
                details = client.get_pair_details(pair_name)
                
                # Verify we have a valid response
                if not isinstance(details, dict):
                    logger.error(f"Invalid response format for pair {pair_name}: {details}")
                    continue
                
                # Create new FuturesPair object with safe type conversion
                try:
                    tick_size = float(details.get('tick_size', 0))
                except (ValueError, TypeError):
                    tick_size = 0.0
                    logger.warning(f"Invalid tick_size for pair {pair_name}, using default")
                
                futures_pair = FuturesPair(
                    pair=pair_name,
                    kind=str(details.get('kind', '')),
                    status=str(details.get('status', '')),
                    tick_size=tick_size,
                    price_band_upper=str(details.get('price_band_upper', ''))
                )
                
                session.add(futures_pair)
                logger.info(f"Successfully processed pair: {pair_name}")
            except Exception as e:
                logger.error(f"Error processing pair {pair_name}: {str(e)}")
                continue
        
        # Commit changes
        session.commit()
        flash('Data refreshed successfully!', 'success')
        return redirect(url_for('index'))
    
    except Exception as e:
        logger.error(f"Error refreshing data: {str(e)}")
        session.rollback()
        flash(f'Error refreshing data: {str(e)}', 'error')
        return redirect(url_for('index'))
    
    finally:
        session.close()

@app.route('/active')
def active_pairs():
    try:
        # Fetch active pairs directly from API
        active_pairs = client.get_active_pairs()
        
        # Process pairs to extract required information
        processed_pairs = []
        for pair in active_pairs:
            if isinstance(pair, dict):
                processed_pair = {
                    'pair': pair.get('pair', ''),
                    'base_currency': pair.get('base_currency', ''),
                    'quote_currency': pair.get('quote_currency', ''),
                    'last_price': pair.get('last_price', '0'),
                    'volume_24h': pair.get('volume_24h', '0')
                }
                processed_pairs.append(processed_pair)
        
        logger.info(f"Retrieved {len(processed_pairs)} active pairs from API")
        return render_template('active_pairs.html', pairs=processed_pairs)
    
    except Exception as e:
        logger.error(f"Error fetching active pairs: {str(e)}")
        flash(f'Error fetching active pairs: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/usdt')
def usdt_pairs():
    try:
        # Fetch USDT pairs directly from API
        usdt_pairs = client.get_usdt_pairs()
        
        # Process pairs to extract required information
        processed_pairs = []
        for pair in usdt_pairs:
            if isinstance(pair, dict):
                processed_pair = {
                    'pair': pair.get('pair', ''),
                    'base_currency': pair.get('base_currency', ''),
                    'last_price': pair.get('last_price', '0'),
                    'high_24h': pair.get('high_24h', '0'),
                    'low_24h': pair.get('low_24h', '0'),
                    'volume_24h': pair.get('volume_24h', '0')
                }
                processed_pairs.append(processed_pair)
        
        logger.info(f"Retrieved {len(processed_pairs)} USDT pairs from API")
        return render_template('usdt_pairs.html', pairs=processed_pairs)
    
    except Exception as e:
        logger.error(f"Error fetching USDT pairs: {str(e)}")
        flash(f'Error fetching USDT pairs: {str(e)}', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(
        debug=os.getenv('FLASK_DEBUG', '0') == '1',
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000))
    )
